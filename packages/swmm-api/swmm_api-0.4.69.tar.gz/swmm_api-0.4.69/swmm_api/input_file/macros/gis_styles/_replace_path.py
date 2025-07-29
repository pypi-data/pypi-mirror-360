from swmm_api.input_file.macros.gis_styles import GIS_STYLE_PATH


def main():
    my_path = '/Users/markus/Nextcloud/GIS/QGIS-swmm-styles/SWMM-icons'
    for fn in GIS_STYLE_PATH.iterdir():
        if fn.suffix in {'.sld', '.qml'}:
            content = fn.read_text()
            if my_path in content:
                content = content.replace(my_path, '__XX__')
                fn.write_text(content)
                # __XX__
                print(fn)
                # break


if __name__ == '__main__':
    main()
