import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


class TestActivities:
    def test_get_root_redirects(self):
        """Test that root redirects to static index.html"""
        # Arrange
        expected_status = 307
        
        # Act
        response = client.get("/", follow_redirects=False)
        
        # Assert
        assert response.status_code == expected_status
        assert "/static/index.html" in response.headers["location"]

    def test_get_activities_returns_list(self):
        """Test that /activities endpoint returns activities"""
        # Arrange
        expected_activities = ["Chess Club", "Programming Class"]
        
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        assert response.status_code == 200
        assert isinstance(activities, dict)
        for activity in expected_activities:
            assert activity in activities

    def test_activity_has_required_fields(self):
        """Test that each activity has required fields"""
        # Arrange
        required_fields = ["description", "schedule", "max_participants", "participants"]
        
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        for name, details in activities.items():
            for field in required_fields:
                assert field in details
            assert isinstance(details["participants"], list)


class TestSignup:
    def test_signup_adds_participant(self):
        """Test that signup adds a participant to an activity"""
        # Arrange
        test_email = "newstudent@mergington.edu"
        activity_name = "Chess%20Club"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={test_email}"
        )
        
        # Assert
        assert response.status_code == 200
        result = response.json()
        assert "message" in result
        assert test_email in result["message"]

    def test_signup_duplicate_fails(self):
        """Test that signing up twice fails with duplicate email"""
        # Arrange
        test_email = "duplicate@mergington.edu"
        activity_name = "Basketball%20Team"
        signup_url = f"/activities/{activity_name}/signup?email={test_email}"
        
        # Act - First signup
        response1 = client.post(signup_url)
        
        # Assert - First signup succeeds
        assert response1.status_code == 200
        
        # Act - Second signup
        response2 = client.post(signup_url)
        
        # Assert - Second signup fails
        assert response2.status_code == 400
        result = response2.json()
        assert "already signed up" in result["detail"].lower()

    def test_signup_nonexistent_activity_fails(self):
        """Test that signing up for non-existent activity returns 404"""
        # Arrange
        test_email = "test@mergington.edu"
        nonexistent_activity = "FakeActivity"
        
        # Act
        response = client.post(
            f"/activities/{nonexistent_activity}/signup?email={test_email}"
        )
        
        # Assert
        assert response.status_code == 404
        result = response.json()
        assert "not found" in result["detail"].lower()


class TestRemoveParticipant:
    def test_remove_participant_succeeds(self):
        """Test that removing a participant successfully removes them"""
        # Arrange
        test_email = "removeme@mergington.edu"
        activity_name = "Tennis%20Club"
        
        # Act - Sign up first
        client.post(f"/activities/{activity_name}/signup?email={test_email}")
        
        # Act - Remove participant
        response = client.delete(
            f"/activities/{activity_name}/participants?email={test_email}"
        )
        
        # Assert
        assert response.status_code == 200
        result = response.json()
        assert "Removed" in result["message"]

    def test_remove_nonexistent_participant_fails(self):
        """Test that removing non-existent participant returns 400"""
        # Arrange
        nonexistent_email = "nonexistent@mergington.edu"
        activity_name = "Art%20Studio"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants?email={nonexistent_email}"
        )
        
        # Assert
        assert response.status_code == 400
        result = response.json()
        assert "not signed up" in result["detail"].lower()

    def test_remove_from_nonexistent_activity_fails(self):
        """Test that removing from non-existent activity returns 404"""
        # Arrange
        test_email = "test@mergington.edu"
        fake_activity = "FakeActivity"
        
        # Act
        response = client.delete(
            f"/activities/{fake_activity}/participants?email={test_email}"
        )
        
        # Assert
        assert response.status_code == 404
        result = response.json()
        assert "not found" in result["detail"].lower()
