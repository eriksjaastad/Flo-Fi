"""
Cost Calculator for AI Render Operations

Calculates costs for different rendering providers (local GPU, Stability AI, DreamStudio)
with precision to prevent explosive costs in batch processing.

USAGE:
    from cost_calculator import CostCalculator
    
    calc = CostCalculator()
    
    # Estimate cost
    cost = calc.estimate_cost(
        provider='stability',
        resolution='1024x1024',
        steps=50,
        model='sdxl',
        count=100
    )
    
    # Validate against limits
    is_safe, message = calc.validate_cost(cost['total'])
"""

import yaml
from pathlib import Path
from typing import Dict, Tuple, Optional


class CostCalculator:
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize cost calculator with pricing config.
        
        Args:
            config_path: Path to cost_config.yaml (optional, uses default if None)
        """
        if config_path is None:
            # Default to shared/cost_config.yaml
            config_path = Path(__file__).parent / "cost_config.yaml"
        
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.providers = self.config['providers']
        self.limits = self.config['limits']
    
    def estimate_cost(
        self, 
        provider: str, 
        resolution: str = '512x512',
        steps: int = 30,
        model: str = 'sd_1_5',
        count: int = 1
    ) -> Dict:
        """
        Estimate cost for rendering operation.
        
        Args:
            provider: Provider name ('local', 'stability', 'dreamstudio')
            resolution: Image resolution (e.g., '1024x1024')
            steps: Number of diffusion steps
            model: Model name (e.g., 'sdxl', 'sd_1_5')
            count: Number of images to generate
            
        Returns:
            Dictionary with cost breakdown:
            {
                'total': float,           # Total cost in USD
                'per_image': float,       # Cost per image
                'count': int,             # Number of images
                'provider': str,          # Provider name
                'breakdown': {            # Detailed breakdown
                    'base': float,
                    'resolution': float,
                    'steps': float,
                    'model': float
                }
            }
        """
        if provider not in self.providers:
            raise ValueError(f"Unknown provider: {provider}. Available: {list(self.providers.keys())}")
        
        provider_config = self.providers[provider]
        
        if provider == 'local':
            # Local GPU rendering - no API cost, only GPU time
            per_image_cost = self._calculate_local_cost(provider_config)
        else:
            # Cloud API rendering (Stability/DreamStudio)
            per_image_cost = self._calculate_api_cost(
                provider_config, 
                resolution, 
                steps, 
                model
            )
        
        total_cost = per_image_cost * count
        
        # Get breakdown details
        breakdown = self._get_cost_breakdown(
            provider, 
            provider_config, 
            resolution, 
            steps, 
            model
        )
        
        return {
            'total': round(total_cost, 4),
            'per_image': round(per_image_cost, 4),
            'count': count,
            'provider': provider,
            'provider_name': provider_config['name'],
            'breakdown': breakdown
        }
    
    def _calculate_local_cost(self, provider_config: Dict) -> float:
        """Calculate cost for local GPU rendering."""
        gpu_cost_per_hr = provider_config['gpu_cost_per_hr']
        avg_time_sec = provider_config['avg_render_time_sec']
        
        # Cost = (time_in_hours) * hourly_rate
        cost_per_image = (avg_time_sec / 3600) * gpu_cost_per_hr
        
        return cost_per_image
    
    def _calculate_api_cost(
        self, 
        provider_config: Dict, 
        resolution: str, 
        steps: int, 
        model: str
    ) -> float:
        """Calculate cost for cloud API rendering."""
        # Base cost
        base_cost = provider_config['base_cost']
        
        # Resolution multiplier
        res_multipliers = provider_config['resolution_multipliers']
        res_multiplier = res_multipliers.get(resolution, 1.0)
        
        # Model multiplier
        models = provider_config.get('models', {})
        model_config = models.get(model, {})
        model_multiplier = model_config.get('cost_multiplier', 1.0)
        
        # Steps cost
        steps_cost_per_step = provider_config['steps_cost_per_step']
        steps_cost = steps * steps_cost_per_step
        
        # Total = base * resolution * model + steps
        total = (base_cost * res_multiplier * model_multiplier) + steps_cost
        
        return total
    
    def _get_cost_breakdown(
        self, 
        provider: str, 
        provider_config: Dict, 
        resolution: str, 
        steps: int, 
        model: str
    ) -> Dict:
        """Get detailed cost breakdown for display."""
        if provider == 'local':
            gpu_cost_per_hr = provider_config['gpu_cost_per_hr']
            avg_time_sec = provider_config['avg_render_time_sec']
            
            return {
                'type': 'local',
                'gpu_cost_per_hr': gpu_cost_per_hr,
                'avg_render_time_sec': avg_time_sec,
                'api_cost': 0.0
            }
        else:
            base = provider_config['base_cost']
            res_mult = provider_config['resolution_multipliers'].get(resolution, 1.0)
            model_mult = provider_config['models'].get(model, {}).get('cost_multiplier', 1.0)
            steps_cost = steps * provider_config['steps_cost_per_step']
            
            return {
                'type': 'api',
                'base_cost': base,
                'resolution': resolution,
                'resolution_multiplier': res_mult,
                'model': model,
                'model_multiplier': model_mult,
                'steps': steps,
                'steps_cost': steps_cost
            }
    
    def validate_cost(
        self, 
        total_cost: float, 
        max_cost: Optional[float] = None
    ) -> Tuple[bool, str]:
        """
        Validate cost against safety limits.
        
        Args:
            total_cost: Total estimated cost in USD
            max_cost: Optional override for max cost (uses config default if None)
            
        Returns:
            Tuple of (is_valid, message)
            - is_valid: True if within limits, False otherwise
            - message: Human-readable message
        """
        if max_cost is None:
            max_cost = self.limits['max_cost_per_job']
        
        warning_threshold = self.limits['warning_threshold']
        
        if total_cost > max_cost:
            return False, f"Cost ${total_cost:.2f} exceeds maximum limit of ${max_cost:.2f}"
        
        if total_cost > warning_threshold:
            return True, f"Warning: Cost ${total_cost:.2f} is above ${warning_threshold:.2f} threshold"
        
        return True, f"Cost ${total_cost:.2f} is within safe limits"
    
    def get_provider_info(self, provider: str) -> Dict:
        """Get information about a specific provider."""
        if provider not in self.providers:
            raise ValueError(f"Unknown provider: {provider}")
        
        return self.providers[provider]
    
    def list_providers(self) -> list:
        """List all available providers."""
        return [
            {
                'id': key,
                'name': config['name'],
                'description': config['description']
            }
            for key, config in self.providers.items()
        ]
    
    def get_resolutions(self, provider: str) -> list:
        """Get available resolutions for a provider."""
        if provider == 'local':
            # Local rendering supports any resolution
            return ['512x512', '768x768', '1024x1024', '1536x1536', '2048x2048']
        
        provider_config = self.providers[provider]
        return list(provider_config['resolution_multipliers'].keys())
    
    def get_models(self, provider: str) -> list:
        """Get available models for a provider."""
        if provider == 'local':
            return []  # Local doesn't use specific models
        
        provider_config = self.providers[provider]
        models = provider_config.get('models', {})
        
        return [
            {
                'id': key,
                'name': config['name']
            }
            for key, config in models.items()
        ]


if __name__ == '__main__':
    # Quick test
    calc = CostCalculator()
    
    print("=== Cost Calculator Test ===\n")
    
    # Test 1: Local rendering
    print("1. Local GPU (100 images):")
    cost = calc.estimate_cost('local', count=100)
    print(f"   Total: ${cost['total']:.2f}")
    print(f"   Per image: ${cost['per_image']:.4f}")
    print()
    
    # Test 2: Stability AI
    print("2. Stability AI SDXL 1024x1024 (100 images, 50 steps):")
    cost = calc.estimate_cost(
        provider='stability',
        resolution='1024x1024',
        steps=50,
        model='sdxl',
        count=100
    )
    print(f"   Total: ${cost['total']:.2f}")
    print(f"   Per image: ${cost['per_image']:.4f}")
    
    # Validate
    is_safe, msg = calc.validate_cost(cost['total'])
    print(f"   {msg}")
    print()
    
    # Test 3: DreamStudio
    print("3. DreamStudio SD 1.5 512x512 (1000 images, 30 steps):")
    cost = calc.estimate_cost(
        provider='dreamstudio',
        resolution='512x512',
        steps=30,
        model='sd_1_5',
        count=1000
    )
    print(f"   Total: ${cost['total']:.2f}")
    print(f"   Per image: ${cost['per_image']:.4f}")
    
    is_safe, msg = calc.validate_cost(cost['total'])
    print(f"   {msg}")

