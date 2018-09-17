from PIL import Image
import numpy as np

import pytest


def test_rgb_handler(use_read_only_database, raster_file, raster_file_xyz):
    import terracotta
    from terracotta.handlers import rgb
    raw_img = rgb.rgb(['val21'], raster_file_xyz, ['val22', 'val23', 'val24'])
    img_data = np.asarray(Image.open(raw_img))
    assert img_data.shape == (*terracotta.get_settings().TILE_SIZE, 3)


def test_rgb_out_of_bounds(use_read_only_database, raster_file):
    import terracotta
    from terracotta.handlers import rgb

    with pytest.raises(terracotta.exceptions.TileOutOfBoundsError) as excinfo:
        rgb.rgb(['val21'], (10, 0, 0), ['val22', 'val23', 'val24'])
        assert 'data covers less than' not in str(excinfo.value)


def test_rgb_lowzoom(use_read_only_database, raster_file, raster_file_xyz_lowzoom):
    import terracotta
    from terracotta.handlers import rgb

    with pytest.raises(terracotta.exceptions.TileOutOfBoundsError) as excinfo:
        rgb.rgb(['val21'], raster_file_xyz_lowzoom, ['val22', 'val23', 'val24'])
        assert 'data covers less than' in str(excinfo.value)


@pytest.mark.parametrize('stretch_range', [[0, 20000], [10000, 20000], [-50000, 50000]])
def test_rgb_stretch(stretch_range, use_read_only_database, read_only_database, raster_file_xyz):
    import terracotta
    from terracotta.xyz import get_tile_data
    from terracotta.handlers import rgb

    ds_keys = ['val21', 'val22']

    raw_img = rgb.rgb(['val21'], raster_file_xyz, ['val22', 'val23', 'val24'],
                      stretch_ranges=[stretch_range] * 3)
    img_data = np.asarray(Image.open(raw_img))[..., 0]

    # get unstretched data to compare to
    driver = terracotta.get_driver(read_only_database)

    tile_x, tile_y, tile_z = raster_file_xyz

    with driver.connect():
        tile_data = get_tile_data(driver, ds_keys, tile_x=tile_x, tile_y=tile_y, tile_z=tile_z,
                                  tilesize=img_data.shape)

    # filter transparent values
    valid_mask = tile_data != 0
    assert np.all(img_data[~valid_mask] == 0)

    valid_img = img_data[valid_mask]
    valid_data = tile_data[valid_mask]

    assert np.all(valid_img[valid_data < stretch_range[0]] == 1)
    stretch_range_mask = (valid_data > stretch_range[0]) & (valid_data < stretch_range[1])
    assert not np.any(np.isin(valid_img[stretch_range_mask], [1, 255]))
    assert np.all(valid_img[valid_data > stretch_range[1]] == 255)
