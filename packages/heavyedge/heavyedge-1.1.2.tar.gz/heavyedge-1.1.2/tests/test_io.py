import numpy as np

from heavyedge import ProfileData, RawProfileCsvs


def test_RawData_dunder(tmp_rawdata_type2_path):
    data = RawProfileCsvs(tmp_rawdata_type2_path)
    assert len(data) == data.count_profiles()

    item = data[np.int64(0)]
    profile = next(data.profiles())
    name = next(data.profile_names())
    assert np.all(item[0] == profile)
    assert item[1] == name

    item = data[:1]
    assert np.all(item[0] == [profile])
    assert np.all(item[1] == [name])

    item = data[np.array([0])]
    assert np.all(item[0] == [profile])
    assert np.all(item[1] == [name])

    item = data[:0]
    assert item[0].size == 0
    assert len(item[1]) == 0


def test_ProfileData_dunder(tmp_prepdata_type2_path):
    with ProfileData(tmp_prepdata_type2_path) as data:
        assert len(data) == data.shape()[0]

        item = data[np.int64(0)]
        profile = data.all_profiles()[0]
        length = len(next(data.profiles()))
        name = next(data.profile_names())
        assert np.all(item[0] == profile)
        assert item[1] == length
        assert item[2] == name

        item = data[:1]
        assert np.all(item[0] == [profile])
        assert np.all(item[1] == [length])
        assert np.all(item[2] == [name])

        item = data[np.array([0])]
        assert np.all(item[0] == [profile])
        assert np.all(item[1] == [length])
        assert np.all(item[2] == [name])

        item = data[:0]
        assert item[0].size == 0
        assert item[1].size == 0
        assert item[2].size == 0
