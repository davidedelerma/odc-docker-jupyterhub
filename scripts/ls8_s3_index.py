import click
from osgeo import osr
import uuid
from datacube.ui import click as ui


def get_geo_ref_points(info):
    return {
        'ul': {'x': info['CORNER_UL_PROJECTION_X_PRODUCT'], 'y': info['CORNER_UL_PROJECTION_Y_PRODUCT']},
        'ur': {'x': info['CORNER_UR_PROJECTION_X_PRODUCT'], 'y': info['CORNER_UR_PROJECTION_Y_PRODUCT']},
        'll': {'x': info['CORNER_LL_PROJECTION_X_PRODUCT'], 'y': info['CORNER_LL_PROJECTION_Y_PRODUCT']},
        'lr': {'x': info['CORNER_LR_PROJECTION_X_PRODUCT'], 'y': info['CORNER_LR_PROJECTION_Y_PRODUCT']},
    }


def get_coords(geo_ref_points, spatial_ref):
    t = osr.CoordinateTransformation(spatial_ref, spatial_ref.CloneGeogCS())

    def transform(p):
        lon, lat, z = t.TransformPoint(p['x'], p['y'])
        return {'lon': lon, 'lat': lat}

    return {key: transform(p) for key, p in geo_ref_points.items()}


def normalise_format_name(n):
    return {
        'geotiff': 'GeoTiff'
    }.get(n.lower(), n)


def parse_ls8(info, path_prefix):
    m = info['PRODUCT_METADATA']
    level = m['DATA_TYPE']
    product_type = 'level1'
    sensing_time = m['DATE_ACQUIRED'] + ' ' + m['SCENE_CENTER_TIME']
    format_name = normalise_format_name(m['OUTPUT_FORMAT'])
    scene_id = info['METADATA_FILE_INFO']['LANDSAT_SCENE_ID']
    station = info['METADATA_FILE_INFO']['STATION_ID']
    sat_path = m['WRS_PATH']
    sat_row = m['WRS_ROW']

    cs_code = 32600 + info['PROJECTION_PARAMETERS']['UTM_ZONE']
    spatial_ref = osr.SpatialReference()
    spatial_ref.ImportFromEPSG(cs_code)

    geo_ref_points = get_geo_ref_points(m)

    images = [('1', 'coastal_aerosol'),
              ('2', 'blue'),
              ('3', 'green'),
              ('4', 'red'),
              ('5', 'nir'),
              ('6', 'swir1'),
              ('7', 'swir2'),
              ('8', 'panchromatic'),
              ('9', 'cirrus'),
              ('10', 'lwir1'),
              ('11', 'lwir2'),
              ('QUALITY', 'quality')]

    return {
        'id': str(uuid.uuid5(uuid.NAMESPACE_URL, path_prefix + '?' + scene_id)),
        'processing_level': level,
        'product_type': product_type,
        # 'creation_dt': ct_time,
        'label': scene_id,
        'platform': {'code': m['SPACECRAFT_ID']},
        'instrument': {'name': m['SENSOR_ID']},
        'acquisition': {'groundstation': {'code': station}},
        'extent': {
            'from_dt': sensing_time,
            'to_dt': sensing_time,
            'center_dt': sensing_time,
            'coord': get_coords(geo_ref_points, spatial_ref),
        },
        'format': {'name': format_name},
        'sat_path': {'begin': sat_path, 'end': sat_path},
        'sat_row': {'begin': sat_row, 'end': sat_row},
        'grid_spatial': {
            'projection': {
                'geo_ref_points': geo_ref_points,
                'spatial_reference': 'EPSG:%s' % cs_code,
            }
        },
        'image': {
            'bands': {
                image[1]: {
                    'path': m['FILE_NAME_BAND_' + image[0]],
                    'layer': 1,
                } for image in images
            }
        },
        'lineage': {'source_datasets': {}},
    }


def ls8_load_all(url):
    import boto3
    import json
    from urllib.parse import urlparse

    url = urlparse(url)

    assert url.scheme == 's3'

    bucket = url.netloc
    prefix = url.path.lstrip('/')

    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucket)

    for o in bucket.objects.filter(Prefix=prefix):
        if o.key.endswith('json'):
            scene_json = json.loads(o.get()['Body'].read().decode('utf-8'))
            json_url = 's3://{}/{}'.format(url.netloc, o.key)
            dir_url = json_url[:json_url.rfind('/')]
            yield json_url, parse_ls8(scene_json['L1_METADATA_FILE'], dir_url)


################################################################################

class IntegerRange(click.ParamType):
    name = 'integer range'

    def convert(self, value, param, ctx):
        if value is None:
            return None

        try:
            vv = tuple(int(v) for v in value.split(':'))
        except ValueError:
            self.fail('%s is not a valid range' % value, param, ctx)

        if len(vv) == 1:
            vv = (vv[0], vv[0])

        if len(vv) > 2:
            self.fail('Expect one of: Int|Int:Int', param, ctx)

        vv = (vv[0], vv[1] + 1)  # Convert to [a,b) range
        return vv


@click.command()
@click.option('--path', type=IntegerRange(), required=True,
              help='Landsat path number or inclusive range, e.g. 10:12')
@click.option('--row', type=IntegerRange(), required=True,
              help='Landsat row number or inclusive range, e.g. 10:12')
@click.option('--base-url',
              default='s3://landsat-pds/c1/L8/',
              help='Use alternative S3 url (default - s3://landsat-pds/c1/L8/)')
@click.option('--product', default='ls8_level1_scene',
              help='Product name to index to')
@ui.verbose_option
@ui.environment_option
@ui.config_option
@ui.pass_datacube()
def ls8_index_main(dc, base_url, path, row, product):
    import itertools
    import datacube

    ds_type = dc.index.products.get_by_name(product)
    if ds_type is None:
        click.echo('Failed to find product "{}"'.format(product))
        click.echo(' Did you run `datacube product add ls8_level1_scene.yaml`?')
        return 1

    if not base_url.endswith('/'):
        base_url += '/'

    for (p, r) in itertools.product(range(*path), range(*row)):
        prefix = '{base_url}{p:03}/{r:03}'.format(base_url=base_url, p=p, r=r)
        click.echo(prefix)

        for (url, doc) in ls8_load_all(prefix):
            click.echo('  ' + url, nl='')
            if url.endswith('RT_MTL.json'):
                click.echo(' -- Skipping RT dataset')
            else:
                ds = datacube.model.Dataset(ds_type, doc, uris=[url], sources={})
                dc.index.datasets.add(ds, sources_policy='skip')
                click.echo(' -- OK')

    return 0

if __name__ == '__main__':
    import sys
    sys.exit(ls8_index_main())
