import multiprocessing

from xcmap.utils import decorator_util, version_util


class PluginManager:
    def __init__(self):
        self.loader = None
        self.processes = {}
        self.start_plugins()

    @staticmethod
    def run_plugin(plugin_name, child_conn):
        # 子进程内独立初始化 PluginLoader
        from xcmap.cores.plugins.loader import PluginLoader
        loader = PluginLoader()
        loader.discover()
        _, plugin = loader.get_plugin(plugin_name)  # 关键：子进程自行加载插件

        data = child_conn.recv()
        print(f'pipe.recv() -> {data}')
        plugin.execute(data)

    def start_plugins(self):
        from xcmap.cores.plugins.loader import PluginLoader
        self.loader = PluginLoader()
        self.loader.discover()
        plugins_dict = self.loader.get_all_plugins()
        for name in plugins_dict.keys():
            parent_conn, child_conn = multiprocessing.Pipe()
            # 改为传递静态方法，避免传递 self
            p = multiprocessing.Process(target=PluginManager.run_plugin, args=(name, child_conn))
            self.processes[name] = (p, parent_conn)
            p.start()

    @decorator_util.retry(2)
    def update_plugin(self, plugin_name, package_name, current_version):
        if plugin_name in self.processes:
            p, conn = self.processes[plugin_name]
            p.terminate()
            p.join()  # 确保旧进程完全退出
            version_util.update_package(package_name, current_version)
            parent_conn, child_conn = multiprocessing.Pipe()
            print(f'plugin_name -> {plugin_name}')
            p = multiprocessing.Process(target=PluginManager.run_plugin, args=(plugin_name, child_conn))
            p.start()
            self.processes[plugin_name] = (p, parent_conn)
            print(f"Updated and restarted {plugin_name}")

    def call_plugin(self, plugin_name, data):
        package_name, plugin = self.loader.get_plugin(plugin_name)
        current_version = version_util.get_current_version(package_name)
        if version_util.check_package_update(package_name, current_version):
            print(f"{package_name} 有更新，正在更新...")
            self.update_plugin(plugin_name, package_name, current_version)
        if plugin_name in self.processes:
            _, conn = self.processes[plugin_name]
            conn.send(data)


# if __name__ == '__main__':
#     manager = PluginManager()
#     plugin_name = 'facebook_account_promotion'
#     manager.call_plugin(plugin_name, '123')
