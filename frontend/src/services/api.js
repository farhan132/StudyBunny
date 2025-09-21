// API service for communicating with the StudyBunny backend
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

class ApiService {
  constructor() {
    this.baseURL = API_BASE_URL;
  }

  // Helper method to get headers
  getHeaders() {
    return {
      'Content-Type': 'application/json',
    };
  }

  // Helper method to handle API responses
  async handleResponse(response) {
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
    }
    return response.json();
  }

  // Task management methods
  async getTasks() {
    try {
      const response = await fetch(`${this.baseURL}/study/tasks/`, {
        method: 'GET',
        headers: this.getHeaders(),
      });
      return await this.handleResponse(response);
    } catch (error) {
      console.error('Error fetching tasks:', error);
      throw error;
    }
  }

  async createTask(taskData) {
    try {
      const response = await fetch(`${this.baseURL}/study/tasks/create/`, {
        method: 'POST',
        headers: this.getHeaders(),
        body: JSON.stringify(taskData),
      });
      return await this.handleResponse(response);
    } catch (error) {
      console.error('Error creating task:', error);
      throw error;
    }
  }

  async updateTask(taskName, updateData) {
    try {
      const response = await fetch(`${this.baseURL}/study/tasks/update-by-name/`, {
        method: 'PATCH',
        headers: this.getHeaders(),
        body: JSON.stringify({
          task_name: taskName,
          ...updateData,
        }),
      });
      return await this.handleResponse(response);
    } catch (error) {
      console.error('Error updating task:', error);
      throw error;
    }
  }

  // Voice agent methods
  async processVoiceCommand(command) {
    try {
      const response = await fetch(`${this.baseURL}/voice/command/`, {
        method: 'POST',
        headers: this.getHeaders(),
        body: JSON.stringify({
          user_id: 3, // Demo user ID
          command_text: command,
        }),
      });
      return await this.handleResponse(response);
    } catch (error) {
      console.error('Error processing voice command:', error);
      throw error;
    }
  }

  // Voice input is now handled by browser Web Speech API
  // This method is kept for backward compatibility but not used
  async captureVoiceInput() {
    throw new Error('Voice input is now handled by browser Web Speech API');
  }

  // Intensity management
  async getIntensity() {
    try {
      const response = await fetch(`${this.baseURL}/core/intensity/`, {
        method: 'GET',
        headers: this.getHeaders(),
      });
      return await this.handleResponse(response);
    } catch (error) {
      console.error('Error getting intensity:', error);
      throw error;
    }
  }

  async setIntensity(intensity) {
    try {
      const response = await fetch(`${this.baseURL}/core/intensity/set/`, {
        method: 'POST',
        headers: this.getHeaders(),
        body: JSON.stringify({ intensity }),
      });
      return await this.handleResponse(response);
    } catch (error) {
      console.error('Error setting intensity:', error);
      throw error;
    }
  }

  // Task progress management
  async updateTaskProgress(taskId, completedSoFar) {
    try {
      const response = await fetch(`${this.baseURL}/study/tasks/${taskId}/progress/`, {
        method: 'PATCH',
        headers: this.getHeaders(),
        body: JSON.stringify({ completed_so_far: completedSoFar }),
      });
      return await this.handleResponse(response);
    } catch (error) {
      console.error('Error updating task progress:', error);
      throw error;
    }
  }

  // Daily schedule methods
  async get14DaySchedule(startDate = null) {
    try {
      let url = `${this.baseURL}/study/get-14-day-schedule/`;
      if (startDate) {
        url += `?start_date=${startDate}`;
      }
      
      const response = await fetch(url, {
        method: 'GET',
        headers: this.getHeaders(),
      });
      return await this.handleResponse(response);
    } catch (error) {
      console.error('Error getting 14-day schedule:', error);
      throw error;
    }
  }

  async generateDailyPlan(date = null) {
    try {
      const response = await fetch(`${this.baseURL}/study/generate-daily-plan/`, {
        method: 'POST',
        headers: this.getHeaders(),
        body: JSON.stringify({ date: date || new Date().toISOString().split('T')[0] }),
      });
      return await this.handleResponse(response);
    } catch (error) {
      console.error('Error generating daily plan:', error);
      throw error;
    }
  }

  // Statistics
  async getStatistics() {
    try {
      const response = await fetch(`${this.baseURL}/study/statistics/`, {
        method: 'GET',
        headers: this.getHeaders(),
      });
      return await this.handleResponse(response);
    } catch (error) {
      console.error('Error getting statistics:', error);
      throw error;
    }
  }

  // Helper method to convert backend task to frontend format
  convertBackendTaskToFrontend(backendTask) {
    return {
      id: backendTask.id,
      name: backendTask.title,
      description: backendTask.description,
      dueDate: backendTask.due_date,
      priority: this.convertDeltaToPriority(backendTask.delta),
      status: backendTask.is_completed ? 'completed' : 'pending',
      estimatedTime: backendTask.T_n,
      completionPercentage: backendTask.completed_so_far,
      created_at: backendTask.created_at,
      updated_at: backendTask.updated_at,
    };
  }

  // Helper method to convert frontend task to backend format
  convertFrontendTaskToBackend(frontendTask) {
    return {
      title: frontendTask.name,
      description: frontendTask.description || '',
      T_n: frontendTask.estimatedTime,
      delta: this.convertPriorityToDelta(frontendTask.priority),
      due_date: frontendTask.dueDate,
      due_time: '12:00:00',
      completed_so_far: frontendTask.completionPercentage || 0,
    };
  }

  // Helper method to convert frontend priority to backend delta
  convertPriorityToDelta(priority) {
    const priorityMap = {
      'low': 1,
      'medium': 2,
      'high': 3,
      'very high': 4,
    };
    return priorityMap[priority] || 2; // Default to medium priority
  }

  // Helper method to convert backend delta to frontend priority
  convertDeltaToPriority(delta) {
    const deltaMap = {
      1: 'low',
      2: 'medium',
      3: 'high',
      4: 'very high',
    };
    return deltaMap[delta] || 'medium';
  }

  // Canvas integration methods
  async syncCanvasTasks() {
    try {
      const response = await fetch('/api/study/canvas/sync/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error syncing Canvas tasks:', error);
      throw error;
    }
  }

  async getCanvasCourses() {
    try {
      const response = await fetch('/api/study/canvas/courses/', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error fetching Canvas courses:', error);
      throw error;
    }
  }

  async getCanvasAssignments(daysAhead = 14) {
    try {
      const response = await fetch(`/api/study/canvas/assignments/?days_ahead=${daysAhead}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error fetching Canvas assignments:', error);
      throw error;
    }
  }

  async getCanvasConfig() {
    try {
      const response = await fetch('/api/study/canvas/config/', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error fetching Canvas config:', error);
      throw error;
    }
  }

  async setCanvasToken(token, baseUrl = 'https://canvas.instructure.com') {
    try {
      const response = await fetch('/api/study/canvas/set-token/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          token: token,
          base_url: baseUrl
        }),
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error setting Canvas token:', error);
      throw error;
    }
  }

  // Notification methods
  async getNotifications() {
    try {
      const response = await fetch(`${this.baseURL}/notifications/`, {
        method: 'GET',
        headers: this.getHeaders(),
      });
      return await this.handleResponse(response);
    } catch (error) {
      console.error('Error fetching notifications:', error);
      throw error;
    }
  }

  async markNotificationRead(notificationId) {
    try {
      const response = await fetch(`${this.baseURL}/notifications/${notificationId}/read/`, {
        method: 'POST',
        headers: this.getHeaders(),
      });
      return await this.handleResponse(response);
    } catch (error) {
      console.error('Error marking notification as read:', error);
      throw error;
    }
  }

  async markAllNotificationsRead() {
    try {
      const response = await fetch(`${this.baseURL}/notifications/mark-all-read/`, {
        method: 'POST',
        headers: this.getHeaders(),
      });
      return await this.handleResponse(response);
    } catch (error) {
      console.error('Error marking all notifications as read:', error);
      throw error;
    }
  }

  async clearAllNotifications() {
    try {
      const response = await fetch(`${this.baseURL}/notifications/clear-all/`, {
        method: 'DELETE',
        headers: this.getHeaders(),
      });
      return await this.handleResponse(response);
    } catch (error) {
      console.error('Error clearing notifications:', error);
      throw error;
    }
  }

  async getNotificationSettings() {
    try {
      const response = await fetch(`${this.baseURL}/notifications/settings/`, {
        method: 'GET',
        headers: this.getHeaders(),
      });
      return await this.handleResponse(response);
    } catch (error) {
      console.error('Error fetching notification settings:', error);
      throw error;
    }
  }

  async updateNotificationSettings(settings) {
    try {
      const response = await fetch(`${this.baseURL}/notifications/settings/`, {
        method: 'POST',
        headers: this.getHeaders(),
        body: JSON.stringify(settings),
      });
      return await this.handleResponse(response);
    } catch (error) {
      console.error('Error updating notification settings:', error);
      throw error;
    }
  }

  async generateTestNotifications() {
    try {
      const response = await fetch(`${this.baseURL}/notifications/generate-test/`, {
        method: 'POST',
        headers: this.getHeaders(),
      });
      return await this.handleResponse(response);
    } catch (error) {
      console.error('Error generating test notifications:', error);
      throw error;
    }
  }
}

// Create and export a singleton instance
const apiService = new ApiService();
export default apiService;
