#!/usr/bin/env python3
"""
🧱 LinkTune Progressive Enhancement Setup
Intelligent installation script for LinkTune enhancement tiers

Guides users through progressive installation based on their needs and system capabilities.
"""

import sys
import subprocess
import platform
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional

def check_system_requirements() -> Dict[str, Any]:
    """Check system capabilities for different tiers"""
    system_info = {
        'platform': platform.system(),
        'python_version': sys.version_info,
        'memory_gb': None,
        'disk_space_gb': None,
        'has_gpu': False,
        'internet_connection': True  # Assume true for now
    }
    
    # Check memory (simplified)
    try:
        if system_info['platform'] == 'Linux':
            with open('/proc/meminfo', 'r') as f:
                meminfo = f.read()
                mem_total = int([line for line in meminfo.split('\n') if 'MemTotal' in line][0].split()[1])
                system_info['memory_gb'] = mem_total / (1024 * 1024)
        else:
            system_info['memory_gb'] = 8  # Conservative estimate
    except:
        system_info['memory_gb'] = 8  # Default
    
    # Check disk space
    try:
        disk_usage = shutil.disk_usage(Path.cwd())
        system_info['disk_space_gb'] = disk_usage.free / (1024**3)
    except:
        system_info['disk_space_gb'] = 10  # Default
    
    # Check for GPU (simplified)
    try:
        result = subprocess.run(['nvidia-smi'], capture_output=True, text=True)
        system_info['has_gpu'] = result.returncode == 0
    except:
        system_info['has_gpu'] = False
    
    return system_info

def assess_tier_compatibility(system_info: Dict[str, Any]) -> Dict[str, str]:
    """Assess which tiers are compatible with the system"""
    compatibility = {}
    
    # Core tier - always compatible
    compatibility['core'] = 'compatible'
    
    # AI tier - needs decent memory and internet
    if system_info['memory_gb'] >= 4 and system_info['internet_connection']:
        compatibility['ai'] = 'compatible'
    elif system_info['memory_gb'] >= 2:
        compatibility['ai'] = 'limited'
    else:
        compatibility['ai'] = 'not_compatible'
    
    # Neural tier - needs lots of memory and preferably GPU
    if system_info['memory_gb'] >= 16 and system_info['disk_space_gb'] >= 10:
        if system_info['has_gpu']:
            compatibility['neural'] = 'optimal'
        else:
            compatibility['neural'] = 'compatible_cpu'
    elif system_info['memory_gb'] >= 8:
        compatibility['neural'] = 'limited'
    else:
        compatibility['neural'] = 'not_compatible'
    
    # Cloud tier - needs internet and API access
    if system_info['internet_connection']:
        compatibility['cloud'] = 'compatible'
    else:
        compatibility['cloud'] = 'not_compatible'
    
    return compatibility

def suggest_installation_plan(compatibility: Dict[str, str], user_needs: Dict[str, Any]) -> List[str]:
    """Suggest installation plan based on compatibility and user needs"""
    plan = ['core']  # Always start with core
    
    # Add AI if compatible and user wants AI features
    if (compatibility['ai'] in ['compatible', 'limited'] and 
        user_needs.get('ai_features', False)):
        plan.append('ai')
    
    # Add neural if compatible and user wants advanced features
    if (compatibility['neural'] in ['optimal', 'compatible_cpu', 'limited'] and
        user_needs.get('advanced_features', False)):
        plan.append('neural')
    
    # Add cloud if compatible and user wants cloud features
    if (compatibility['cloud'] == 'compatible' and
        user_needs.get('cloud_features', False)):
        plan.append('cloud')
    
    return plan

def install_tier(tier: str, verbose: bool = True) -> bool:
    """Install a specific tier"""
    if verbose:
        print(f"🧱 Installing LinkTune {tier} tier...")
    
    try:
        if tier == 'core':
            cmd = [sys.executable, '-m', 'pip', 'install', '.']
        else:
            cmd = [sys.executable, '-m', 'pip', 'install', f'.[{tier}]']
        
        if verbose:
            print(f"Running: {' '.join(cmd)}")
        
        result = subprocess.run(cmd, capture_output=not verbose, text=True)
        
        if result.returncode == 0:
            if verbose:
                print(f"✅ {tier} tier installed successfully!")
            return True
        else:
            if verbose:
                print(f"❌ {tier} tier installation failed")
                if not verbose and result.stderr:
                    print(f"Error: {result.stderr}")
            return False
            
    except Exception as e:
        if verbose:
            print(f"❌ Installation error: {e}")
        return False

def interactive_setup():
    """Interactive setup wizard"""
    print("🎵 Welcome to LinkTune Progressive Enhancement Setup!")
    print("=" * 60)
    
    # Check system
    print("🔍 Checking system requirements...")
    system_info = check_system_requirements()
    compatibility = assess_tier_compatibility(system_info)
    
    print(f"\n📊 System Information:")
    print(f"   Platform: {system_info['platform']}")
    print(f"   Python: {system_info['python_version'].major}.{system_info['python_version'].minor}")
    print(f"   Memory: {system_info['memory_gb']:.1f} GB")
    print(f"   GPU: {'Available' if system_info['has_gpu'] else 'Not detected'}")
    
    print(f"\n🧱 Tier Compatibility:")
    tier_status = {
        'compatible': '✅ Fully compatible',
        'optimal': '🚀 Optimal performance',
        'compatible_cpu': '⚡ CPU-only compatible',
        'limited': '⚠️  Limited compatibility',
        'not_compatible': '❌ Not compatible'
    }
    
    for tier, status in compatibility.items():
        print(f"   {tier.capitalize()}: {tier_status.get(status, status)}")
    
    # Get user preferences
    print(f"\n🎯 What do you want to do with LinkTune?")
    print("1. Basic link-to-music conversion (core tier)")
    print("2. AI-enhanced composition with ChatMusician (ai tier)")
    print("3. Advanced neural synthesis with Orpheus (neural tier)")
    print("4. Cloud execution with auto-scaling (cloud tier)")
    print("5. Everything - I want it all! (full installation)")
    print("6. Custom selection")
    
    while True:
        try:
            choice = input("\nEnter your choice (1-6): ").strip()
            if choice in ['1', '2', '3', '4', '5', '6']:
                break
            print("Please enter a number between 1 and 6")
        except KeyboardInterrupt:
            print("\n\n👋 Installation cancelled by user")
            return
    
    # Determine installation plan
    if choice == '1':
        install_plan = ['core']
    elif choice == '2':
        install_plan = ['core', 'ai'] if compatibility['ai'] != 'not_compatible' else ['core']
    elif choice == '3':
        install_plan = ['core', 'ai', 'neural'] if compatibility['neural'] != 'not_compatible' else ['core', 'ai']
    elif choice == '4':
        install_plan = ['core', 'cloud'] if compatibility['cloud'] == 'compatible' else ['core']
    elif choice == '5':
        install_plan = []
        for tier in ['core', 'ai', 'neural', 'cloud']:
            if compatibility[tier] not in ['not_compatible']:
                install_plan.append(tier)
    else:  # choice == '6'
        install_plan = custom_selection(compatibility)
    
    # Show installation plan
    print(f"\n📋 Installation Plan:")
    for tier in install_plan:
        status = compatibility.get(tier, 'unknown')
        print(f"   🧱 {tier.capitalize()} tier - {tier_status.get(status, status)}")
    
    # Confirm installation
    confirm = input(f"\n🚀 Proceed with installation? (y/N): ").strip().lower()
    if confirm not in ['y', 'yes']:
        print("👋 Installation cancelled")
        return
    
    # Install tiers
    print(f"\n🔧 Installing LinkTune...")
    success_count = 0
    
    for i, tier in enumerate(install_plan):
        if install_tier(tier):
            success_count += 1
        else:
            print(f"⚠️  Continuing with remaining tiers...")
    
    # Final status
    print(f"\n🎉 Installation Complete!")
    print(f"   Successfully installed: {success_count}/{len(install_plan)} tiers")
    
    if success_count > 0:
        print(f"\n🎵 Try LinkTune now:")
        print(f"   linktune https://example.com")
        if 'ai' in install_plan[:success_count]:
            print(f"   linktune https://example.com --ai chatmusician")
        print(f"   linktune --help")
    
    print(f"\n📚 Next steps:")
    print(f"   • Run 'linktune --test' to verify installation")
    print(f"   • Run 'linktune --list-tiers' to see available features") 
    print(f"   • Check documentation for configuration options")

def custom_selection(compatibility: Dict[str, str]) -> List[str]:
    """Allow custom tier selection"""
    available_tiers = []
    for tier, status in compatibility.items():
        if status != 'not_compatible':
            available_tiers.append(tier)
    
    print(f"\n🎯 Available tiers for your system:")
    for i, tier in enumerate(available_tiers, 1):
        status = compatibility[tier]
        print(f"{i}. {tier.capitalize()} tier - {status}")
    
    selected = []
    while True:
        try:
            selection = input(f"\nSelect tiers (comma-separated numbers, e.g., 1,2): ").strip()
            if not selection:
                break
            
            indices = [int(x.strip()) - 1 for x in selection.split(',')]
            selected = [available_tiers[i] for i in indices if 0 <= i < len(available_tiers)]
            
            if selected:
                break
            print("Invalid selection, please try again")
            
        except (ValueError, IndexError):
            print("Invalid input, please enter numbers separated by commas")
        except KeyboardInterrupt:
            return ['core']  # Default fallback
    
    return selected or ['core']

def quick_install(tier: str = 'ai'):
    """Quick installation for specific tier"""
    print(f"🚀 Quick installing LinkTune {tier} tier...")
    
    system_info = check_system_requirements()
    compatibility = assess_tier_compatibility(system_info)
    
    tiers_to_install = ['core']
    if tier != 'core':
        if compatibility[tier] != 'not_compatible':
            tiers_to_install.append(tier)
        else:
            print(f"❌ {tier} tier not compatible with your system")
            print(f"🔄 Installing core tier only")
    
    success = True
    for tier_name in tiers_to_install:
        if not install_tier(tier_name, verbose=True):
            success = False
            break
    
    if success:
        print(f"\n✅ LinkTune installation complete!")
        print(f"🎵 Try: linktune https://example.com")
    else:
        print(f"\n❌ Installation failed")
        return False
    
    return True

if __name__ == '__main__':
    if len(sys.argv) > 1:
        tier = sys.argv[1]
        quick_install(tier)
    else:
        interactive_setup()