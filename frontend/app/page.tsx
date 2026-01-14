"use client";

import { use, useEffect, useState } from "react"
import Select from 'react-select'

export default function Home() {
  const text = "Testing Testing";
  const [player1, setPlayer1] = useState("");
  const [player2, setPlayer2] = useState("");

  const [testing, setTesting] = useState("");
  const [confidence, setConfidence] = useState("")

  const [avgFP1, setAvgFP1] = useState(0)
  const [momentum1, setMomentum1] = useState(0)
  const [td1, setTd1] = useState(0)
  const [position1, setPosition1] = useState("")
  const [team1, setTeam1] = useState("")
  const [epa1, setEpa1] = useState(0)
  const [posStat1, setPosStat1] = useState("")

  const [avgFP2, setAvgFP2] = useState(0)
  const [momentum2, setMomentum2] = useState(0)
  const [td2, setTd2] = useState(0)
  const [position2, setPosition2] = useState("")
  const [team2, setTeam2] = useState("")
  const [epa2, setEpa2] = useState(0)
  const [posStat2, setPosStat2] = useState("")

  const [week, setWeek] = useState(4)

  const positions = ["QB", "WR", "RB", "TE", "All"]
  const [players, setPlayers] = useState(null)

  const [filter, setFilter] = useState("All")

  const [selectPlayers, setSelectPlayers] = useState([]) 

  const options = [
    { value: 'chocolate', label: 'Chocolate' },
    { value: 'strawberry', label: 'Strawberry' },
    { value: 'vanilla', label: 'Vanilla' }
  ]

  async function submit() {
    const res = await fetch("http://127.0.0.1:5000", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ player1, player2, week})
    });

    const data = await res.json();
    if(data.status === 'failed' || data.data === null) {
      setTesting("No player found or no data for player (injuries this season or has not made an appearance)")
      setConfidence("")
    }
    else {
      setAvgFP1(data.display1['average_fantasy_points'].toFixed(2))
      setPosition1(data.display1['position'])
      console.log(position1)
      setTd1(data.display1['td_rate'].toFixed(2))
      setMomentum1(data.display1['recent_momentum'].toFixed(2))
      if(data.display1['position'] === "QB") {
        setPosStat1("Average Passing Yards: " + data.display1['average_passing_yards'].toFixed(2))
      }
      else if(data.display1['position'] === "RB") {
        setPosStat1("Average Rushing Yards: " + data.display1['average_rushing_yards'].toFixed(2))
      }
      else if(data.display1['position'] === "WR" || data.display1['position'] === "TE") {
        setPosStat1("Average Recieving Yards: " + data.display1['average_recieving_yards'].toFixed(2))
      }
      else {
        setPosStat1("")
      }
      setEpa1(data.display1['epa_per_play'].toFixed(2))
      setTeam1(data.display1['team'])
      //------------------------------------------------------------
      setAvgFP2(data.display2['average_fantasy_points'].toFixed(2))
      setPosition2(data.display2['position'])
      console.log(position2)
      setTd2(data.display2['td_rate'].toFixed(2))
      setMomentum2(data.display2['recent_momentum'].toFixed(2))
      if(data.display2['position'] === "QB") {
        setPosStat2("Average Passing Yards: " + data.display2['average_passing_yards'].toFixed(2))
      }
      else if(data.display2['position'] === "RB") {
        setPosStat2("Average Rushing Yards: " + data.display2['average_rushing_yards'].toFixed(2))
      }
      else if(data.display2['position'] === "WR" || data.display2['position'] === "TE") {
        setPosStat2("Average Recieving Yards: " + data.display2['average_recieving_yards'].toFixed(2))
      }
      else {
        setPosStat2("")
      }
      setEpa2(data.display2['epa_per_play'].toFixed(2))
      if(data.data['recommended_player'] === 1) {
        setTesting("We recommend player " + player1 + ",")
      }
      else {
        setTesting("We recommend player " + player2 + ",")
      }
      setTeam2(data.display2['team'])
      setConfidence(" with a confidence " + (data.data['confidence']).toFixed(2) + " percent")
      
    }
  }
  console.log("Starting render")
  useEffect(() => {
    fetch('http://127.0.0.1:5000/top-players')
          .then(response => response.json())
          .then(data => {
              if (data.status === 'success') {
                setPlayers(data.data)
              } 
          })
          .catch(err => {
              console.log("Err")
          });
  }, []);

  useEffect(() => {
    fetch('http://127.0.0.1:5000/players')
          .then(response => response.json())
          .then(data => {
            const option = data.data.map(p => ({
              value: `${p.first_name} ${p.last_name}`,
              label: `${p.first_name} ${p.last_name} ${p.position} - ${p.team}`,
              player: p
            }));
            setSelectPlayers(option)
          });
  }, []);

  if (!players) {
      return <div>Loading...</div>;
  }
  if (!players[filter]) return <div>No data for {filter}</div>;

  return (
    <div className="min-h-screen flex flex-col">
      {/* Top Header/Title */}
      <header className="bg-gray-500 text-white p-6 text-center">
        <h1 className="text-4xl font-bold">Fantasy Football Start/Sit Calculator</h1>
      </header>
      
      {/* Main Content Area with Sidebar */}
      <div className="flex flex-1">
        {/* Left Sidebar */}
        <aside className="w-64 bg-gray-100 p-6">
          <h2 className="text-xl font-semibold mb-4">Player Statistics</h2>
          <div className="border-3 border-black rounded-xl h-1/3 text-[14px]">
            <p className="p-2">Player 1: {player1}, {position1}</p>
            <p className="p-2">Average fantasy points: {avgFP1}</p>
            <p className="p-2">3 week average: {momentum1}</p>
            <p className="p-2">Average td/g: {td1}</p>
            <p className="p-2">{team1} epa: {epa1}</p>
            <p className="p-2">{posStat1}</p>
          </div>
          <p>---------------------------------------</p>
          <div className="border-3 border-black rounded-xl h-1/3 text-[14px]">
            <p className="p-2">Player 2: {player2}, {position2}</p>
            <p className="p-2">Average fantasy points: {avgFP2}</p>
            <p className="p-2">3 week average: {momentum2}</p>
            <p className="p-2">Average td/g: {td2}</p>
            <p className="p-2">{team2} epa: {epa2}</p>
            <p className="p-2">{posStat2}</p>
          </div>
        </aside>
        
        {/* Main Content */}
        <main className="flex-1 p-8 text-center">
          <h2 className="text-2xl mb-8">Main Content</h2>
          <div>            
            <select
              value={week}
              onChange={(e) => setWeek(Number(e.target.value))}
              className="border rounded px-3 py-2"
            >
              {Array.from({ length: 15 }, (_, i) => i + 4).map((w) => (
                <option key={w} value={w}>
                  Week {w}
                </option>
              ))}
            </select>
          </div>
          <Select options={selectPlayers} 
                  value={player1.first_name}
                  onChange={(e) => {
                    if(e) {
                      setPlayer1(e.value);
                    }
                    else {
                      setPlayer1('')
                    }
                  }}
                  placeholder="Enter player name"
                  isSearchable={true}
                  isClearable={true}
                  className="w-1/4 mx-auto p-3"
                />

          <Select options={selectPlayers} 
                  value={player2.first_name}
                  onChange={(e) => {
                    if(e) {
                      setPlayer2(e.value);
                    }
                    else {
                      setPlayer2('')
                    }
                  }}
                  placeholder="Enter player name"
                  isSearchable={true}
                  isClearable={true}
                  className="w-1/4 mx-auto p-3"
                />
          <button className="bg-blue-500 text-white px-6 py-2 rounded hover:bg-blue-600"
            onClick={submit}>
            Submit
          </button>
          <div className="w-1/2 p-3 mx-auto">
            <p className="text-xl p-12 border-3 border-black rounded-xl">{testing}{confidence}</p>
          </div>
          <div className="w-1/2 p-3 mx-auto">
            <p className="text-l p-5 border-3 border-black rounded-xl bg-cyan-500 text-left">Note: Due to the football season's conclusion, this application's full ability can't be 
              utilized until the 2026 season starts. Until then feel free to test player stats and model prediction on a week-by-week basis!</p>
          </div>
          
        </main>
        
        {/* Right Sidebar */}
        <aside className="w-64 bg-gray-100 p-6">
          <h2 className="text-xl font-semibold mb-4">Top Players This Season</h2>
          <select
            value={filter}
            onChange={(e) => {
              setFilter(String(e.target.value))
            }}
            className="border rounded px-1 py-.5">
              {positions.map((pos) => (
                <option key={pos} value={pos}>{pos}</option>
              ))}
          </select>
          <p>---------------------------------------</p>
          <div className="border-3 border-black rounded-xl h-2/3 text-[12px]">
              {players[filter].map((player, index) => (
                    <div key={player.abbreviation}>
                        {index + 1}. {player.abbreviation} - {player.team} ({player.position}) - {player.fantasy_points.toFixed(1)} pts
                    </div>
                ))}
          </div>
        </aside>
      </div>
    </div>
  );
}
