# Favorite Places Backend

This project is a Flask-based backend service for managing favorite places, designed for collaborative educational projects. It allows storing and retrieving details about favorite locations, such as names of the students, coordinates, reasons, activities, memories, and images.

## Features

- **Add Places**: Store information about a favorite place, including the name, coordinates, emoji, and more.
- **Retrieve Places**: Fetch all favorite places with complete details in JSON format.
- **Collaborative**: Designed to support educational activities, enabling students to share their favorite places.
- **Image Support**: Includes an option to attach image URLs to places.
- **Scalable**: Built with Flask and SQLAlchemy for easy integration and scalability.

## Technologies Used

- **Programming Language**: Python 3
- **Framework**: Flask
- **Database**: SQLAlchemy (SQLite as default)

## API Endpoints

### GET `/`
Fetches all favorite places.

#### Response Example
```json
[
  {
    "student": "JohnDoe",
    "place": "Disneyland",
    "coordinates": "33.8121,-117.9190",
    "reason": "Amazing rides",
    "emoji": "🏰",
    "activity": "Roller Coasters",
    "memory": "First trip with friends",
    "companions": "Family",
    "image_url": "https://example.com/image.jpg"
  }
]
```

### POST `/add`
Adds a new favorite place.

#### Request Example
```json
{
  "student": "JohnDoe",
  "place": "Disneyland",
  "coordinates": "33.8121,-117.9190",
  "reason": "Amazing rides",
  "emoji": "🏰",
  "activity": "Roller Coasters",
  "memory": "First trip with friends",
  "companions": "Family",
  "image_url": "https://example.com/image.jpg"
}
```

#### Response Example
```json
{
  "message": "Place added successfully!"
}
```

## How to Run Locally

### Prerequisites
- Python 3.8+
- pip

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/fav-places-backend.git
   cd fav-places-backend
   ```

2. Create a virtual environment and activate it:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the application:
   ```bash
   flask run
   ```

5. Access the API at `http://127.0.0.1:5000/`.

## Deployment

The project is prepared for deployment on Google Cloud. To deploy:

1. Ensure you have the Google Cloud CLI installed and authenticated.
2. Deploy the application:
   ```bash
   gcloud run deploy --source .
   ```

## Project Structure

```
.
├── app.py                 # Main application file
├── models.py              # Database models
├── requirements.txt       # Python dependencies
├── README.md              # Project documentation
├── migrations/            # Database migrations (if any)
└── static/                # Static assets (optional)  
```

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request for review.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

