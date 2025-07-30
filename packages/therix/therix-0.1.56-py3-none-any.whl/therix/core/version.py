import pkg_resources    



def get_current_version():
        library_name = 'therix'
        version = pkg_resources.get_distribution(library_name).version
        return version

async def async_get_current_version():
        library_name = 'therix'
        version = pkg_resources.get_distribution(library_name).version
        return version