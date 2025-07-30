import importlib.util
import importlib.machinery
from pathlib import Path
from typing import Dict, List, Optional
from sunra_apispec.base.adapter_interface import BaseAdapter
from sunra_apispec.base.common import RequestType

class RegistryItem:
    def __init__(
            self,
            adapter: BaseAdapter,
            service_provider: str,
            request_type: RequestType
    ):
        self.adapter = adapter
        self.service_provider = service_provider
        self.request_type = request_type


class ModelRegistry:
    def __init__(self):
        self.registries: Dict[str, List[RegistryItem]] = {}
        self._initialize_registries()
    
    def _initialize_registries(self):
        current_dir = Path(__file__).parent
        specs_dir = current_dir / "specs"
        
        for provider_dir in specs_dir.iterdir():
            if not provider_dir.is_dir():
                continue
            
            for model_dir in provider_dir.iterdir():
                if not model_dir.is_dir():
                    continue
                
                endpoints_file = model_dir / "endpoints.py"
                if not endpoints_file.exists():
                    continue
                
                try:
                    module_name = f"sunra_apispec.specs.{provider_dir.name}.{model_dir.name}.endpoints"
                    
                    spec = importlib.util.spec_from_file_location(module_name, endpoints_file)
                    if spec and spec.loader:
                        module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(module)
                        
                        if hasattr(module, "registry_items"):
                            registry_items = getattr(module, "registry_items")
                            for model_endpoint, items in registry_items.items():
                                self.registries[model_endpoint] = []
                                for item in items:
                                    self.registries[model_endpoint].append(
                                        RegistryItem(
                                            adapter=item['adapter'],
                                            service_provider=item['service_provider'],
                                            request_type=item['request_type']
                                        )
                                    )
                                
                except Exception as e:
                    print(f"Error importing {endpoints_file}: {e}")

    def get(self, model_endpoint: str, service_provider: str) -> Optional[RegistryItem]:
        if model_endpoint not in self.registries:
            return None
        
        registry_items = self.registries[model_endpoint]

        for item in registry_items:
            if item.service_provider == service_provider:
                return item
        
        return None

    def get_registries(self) -> Dict[str, List[RegistryItem]]:
        return self.registries

