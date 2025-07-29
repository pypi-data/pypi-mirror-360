"""Tests for the UrbanFeatureExtractor class."""

import pytest
from unittest.mock import patch, MagicMock

from geofeaturekit.core.extractor import UrbanFeatureExtractor
from geofeaturekit.exceptions.errors import GeoFeatureKitError
from geofeaturekit import features_from_location

def test_extractor_initialization():
    """Test basic initialization of UrbanFeatureExtractor."""
    extractor = UrbanFeatureExtractor()
    assert extractor.radius_meters == 500
    assert extractor.use_cache is True
    assert extractor.cache_dir.endswith('/cache')

def test_invalid_radius():
    """Test that invalid radius raises GeoFeatureKitError."""
    with pytest.raises(GeoFeatureKitError):
        UrbanFeatureExtractor(radius_meters=-100)

def test_single_location():
    """Test extracting features for a single location."""
    extractor = UrbanFeatureExtractor()
    features = extractor.features_from_location(40.7128, -74.0060)  # NYC
    assert isinstance(features, dict)
    assert 'network_metrics' in features
    assert 'poi_metrics' in features

def test_batch_locations():
    """Test extracting features for multiple locations."""
    extractor = UrbanFeatureExtractor()
    locations = [
        (40.7128, -74.0060),  # NYC
        (51.5074, -0.1278),   # London
    ]
    features = extractor.features_from_location_batch(locations)
    assert isinstance(features, list)
    assert len(features) == len(locations)
    for feature in features:
        assert isinstance(feature, dict)
        assert 'network_metrics' in feature
        assert 'poi_metrics' in feature

def test_features_from_location():
    """Test detailed output structure from features_from_location."""
    extractor = UrbanFeatureExtractor()
    features = extractor.features_from_location(40.7128, -74.0060)  # NYC
    
    # Check main sections
    assert 'network_metrics' in features
    assert 'poi_metrics' in features
    assert 'pedestrian_network' in features
    assert 'land_use_metrics' in features
    assert 'data_quality_metrics' in features
    
    # Check network metrics structure
    network = features['network_metrics']
    assert 'basic_metrics' in network
    assert 'density_metrics' in network
    assert 'connectivity_metrics' in network
    assert 'street_pattern_metrics' in network
    
    # Check POI metrics structure
    pois = features['poi_metrics']
    assert 'absolute_counts' in pois
    assert 'density_metrics' in pois
    assert 'distribution_metrics' in pois

def test_features_from_location_batch():
    """Test batch processing with detailed output structure."""
    extractor = UrbanFeatureExtractor()
    locations = [
        (40.7128, -74.0060),  # NYC
        (51.5074, -0.1278),   # London
    ]
    features_list = extractor.features_from_location_batch(locations)
    
    assert len(features_list) == len(locations)
    for features in features_list:
        # Check main sections
        assert 'network_metrics' in features
        assert 'poi_metrics' in features
        assert 'pedestrian_network' in features
        assert 'land_use_metrics' in features
        assert 'data_quality_metrics' in features

def test_features_from_location_batch():
    """Test batch processing with detailed output structure."""
    extractor = UrbanFeatureExtractor()
    locations = [
        (40.7128, -74.0060),  # NYC
        (51.5074, -0.1278),   # London
    ]
    features_list = extractor.features_from_location_batch(locations)
    
    assert len(features_list) == len(locations)
    for features in features_list:
        # Check main sections
        assert 'network_metrics' in features
        assert 'poi_metrics' in features
        assert 'pedestrian_network' in features
        assert 'land_use_metrics' in features
        assert 'data_quality_metrics' in features 