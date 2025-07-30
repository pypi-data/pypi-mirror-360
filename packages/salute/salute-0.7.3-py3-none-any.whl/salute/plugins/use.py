from pygments.plugin import iter_entry_points
from importlib.metadata import entry_points


def use_plugins():
    print("DEBUGER")
    print(iter_entry_points)
    for entry_point in iter_entry_points("salute.plugins"):
        current_entry_point = entry_point.load()

        print("CURRENT ENTRYPOINT: ", current_entry_point)

    print("DEBUG # 2")
    discovered_plugins = entry_points(group="salute.plugins")
    print("discovered plugins: ", discovered_plugins)


print(use_plugins())
