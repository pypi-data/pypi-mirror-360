import yaml
import importlib.resources as pkg_resources  # chuẩn mới
import infra_analytics  # import đúng package của bạn

def get_config():
    with pkg_resources.files(infra_analytics).joinpath("config.yaml").open("r") as cf:
        config = yaml.load(cf, Loader=yaml.SafeLoader)
    return config

infra_analytics_config = None
