# Build information - tier is determined at runtime based on license
BUILD_EDITION = 'universal'  # Single build for all tiers
VERSION = 'dev-20250705-1212'
BUILD_TIME = '2025-07-05T12:12:07Z'
BUILD_COMMIT = '34bbc396557507b5d73fc113755ccc49b330748c'

# License tiers are determined at runtime by checking the license
# This allows the same binary to work with different license tiers
AVAILABLE_TIERS = ['free', 'pro', 'enterprise']
