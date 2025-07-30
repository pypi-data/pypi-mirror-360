# Build information - tier is determined at runtime based on license
BUILD_EDITION = 'universal'  # Single build for all tiers
VERSION = 'dev-20250708-1846'
BUILD_TIME = '2025-07-08T18:46:27Z'
BUILD_COMMIT = 'f8ba32ea9fd70da4540c114ec278fa2706ccbed7'

# License tiers are determined at runtime by checking the license
# This allows the same binary to work with different license tiers
AVAILABLE_TIERS = ['free', 'pro', 'enterprise']
