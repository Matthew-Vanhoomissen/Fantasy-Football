# Fantasy Football Start/Sit Calculator 🏈

A full-stack machine learning application that helps fantasy football players make data-driven start/sit decisions with confidence scores.

## 🌐 Live Demo

**Link:** [https://fantasy-football-7w2a.vercel.app](https://fantasy-football-7w2a.vercel.app)  

## ✨ Features

- **Player Comparison**: Compare two players head-to-head with detailed statistics
- **ML-Powered Predictions**: XGBoost model provides recommendations with confidence scores
- **Advanced Metrics**: 
  - Expected Points Added (EPA)
  - 3-week momentum tracking
  - Boom/bust analysis
  - Matchup advantages
  - Usage rates and target share
- **Real-Time Stats**: Top 20 players by position updated for the 2025 season
- **Responsive Design**: Optimized for both desktop and mobile devices
- **PPR Scoring**: Follows standard PPR (Point Per Reception) fantasy scoring

## 🛠️ Tech Stack

### Frontend
- **Framework**: Next.js 14 (React 18)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **UI Components**: react-select
- **Deployment**: Vercel
- **Analytics**: Vercel Analytics

### Backend
- **Framework**: Flask (Python 3.13)
- **ML Library**: XGBoost, scikit-learn
- **Data Processing**: pandas, numpy
- **Deployment**: Render
- **Server**: Gunicorn

### Data Sources
- **Play-by-Play Data**: nflfastr (via nflverse)
- **Player Information**: Ball Don't Lie API
- **Fantasy Points**: Custom calculation engine

## 📊 Machine Learning Pipeline

### Data Collection
```python
# 40,000+ NFL play-by-play records from 2025 season
- Offensive plays (pass/run)
- Player statistics (passing, rushing, receiving)
- Defensive metrics (EPA allowed, points against)
- Team efficiency ratings
```

### Feature Engineering (20+ Features)
```python
Player Features:
- average_fantasy_points
- recent_momentum (3-week average)
- boom_percent / bust_percent
- boom_points_average / bust_points_average
- passing/rushing/receiving averages
- TD rates

Team Features:
- epa_per_play
- pass_epa / rush_epa
- points_against
- offensive efficiency

Matchup Features:
- matchup_advantage (team EPA - opponent EPA)
- total_usage (target % + carry %)
- boom_bust_ratio

Variance Features:
- recent_volatility
- boom_potential
- bust_risk
- variance_score
```

### Model
- **Algorithm**: XGBoost Classifier
- **Task**: Binary classification (recommend player 1 vs player 2)
- **Output**: Prediction + confidence score
- **Training**: Historical player performance data

## 🔧 API Endpoints

### `GET /top-players`
Returns top 20 players by position for the 2025 season.

**Response:**
```json
{
  "status": "success",
  "data": {
    "QB": [...],
    "RB": [...],
    "WR": [...],
    "TE": [...],
    "All": [...]
  }
}
```

### `GET /players`
Returns all offensive players with team and position.

**Response:**
```json
{
  "status": "success",
  "data": [
    {
      "first_name": "Patrick",
      "last_name": "Mahomes",
      "team": "KC",
      "position": "QB"
    },
    ...
  ]
}
```

### `POST /`
Compares two players and returns prediction.

**Request:**
```json
{
  "player1": "Patrick Mahomes",
  "player2": "Josh Allen",
  "week": 10
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "recommended_player": 1,
    "confidence": 67.8
  },
  "display1": {
    "average_fantasy_points": 24.5,
    "position": "QB",
    "team": "KC",
    ...
  },
  "display2": {...}
}
```

## 📈 Data Pipeline

1. **Collection**: Fetch NFL play-by-play data via nflfastr
2. **Cleaning**: Filter for offensive plays, remove penalties/special teams
3. **Aggregation**: Calculate per-player and per-team statistics
4. **Feature Engineering**: Create 20+ features for ML model
5. **Training**: Train XGBoost model on historical comparisons
6. **Serving**: Flask API serves real-time predictions

## 🎯 Fantasy Scoring (PPR)
```
Passing: 0.04 pts/yard, 4 pts/TD, -2 pts/INT
Rushing: 0.1 pts/yard, 6 pts/TD
Receiving: 0.1 pts/yard, 6 pts/TD, 1 pt/reception
2-Point Conversions: 2 pts
Fumbles Lost: -2 pts
```

## 🚧 Deployment

### Backend (Render)
- Free tier: 512MB RAM, sleeps after 15min inactivity
- Auto-deploys on push to `main` branch
- Environment variables configured in Render dashboard

### Frontend (Vercel)
- Serverless deployment
- Auto-deploys on push to `main` branch
- Environment variable: `NEXT_PUBLIC_API_URL`

## 👤 Author

**Matthew Vanhoomissen**

- LinkedIn: [matthew-vanhoomissen](https://www.linkedin.com/in/matthew-vanhoomissen-b9669b325/)
- GitHub: [@Matthew-Vanhoomissen](https://github.com/Matthew-Vanhoomissen)
- Email: ma.vanhoom1@gmail.com

## 🙏 Acknowledgments

- [nflfastr](https://www.nflfastr.com/) for comprehensive NFL play-by-play data
- [Ball Don't Lie API](https://www.balldontlie.io/) for player roster data

## 📊 Performance Notes

- First request after 15min may take 30-60s (free tier cold start)
- Subsequent requests are typically < 2s
- Dataset covers 2025 NFL season (weeks 1-18)
- Model trained on 1000+ player comparisons