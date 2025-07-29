# Build information - tier is determined at runtime based on license
BUILD_EDITION = 'universal'  # Single build for all tiers
VERSION = 'main'
BUILD_TIME = '2025-07-05T22:03:17Z'
BUILD_COMMIT = '9c11dc6ededd18eb6ad8add1ce46c967da406cf9'

# License tiers are determined at runtime by checking the license
# This allows the same binary to work with different license tiers
AVAILABLE_TIERS = ['free', 'pro', 'enterprise']
