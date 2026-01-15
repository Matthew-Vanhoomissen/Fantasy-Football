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
      setTesting("No player found or no data for player (injuries this season or has not made an appearance) or selected week is players bye week")
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

  const selectStyles = {
    control: (base) => ({
      ...base,
      borderColor: '#3b82f6',
      boxShadow: 'none',
      '&:hover': {
        borderColor: '#1e40af'
      }
    }),
    option: (base, state) => ({
      ...base,
      backgroundColor: state.isSelected ? '#3b82f6' : state.isFocused ? '#dbeafe' : 'white',
      color: state.isSelected ? 'white' : '#1e293b',
    })
  };

  if (!players) {
      return <div>Loading...</div>;
  }
  if (!players[filter]) return <div>No data for {filter}</div>;

  return (
    <div className="min-h-screen flex flex-col">
      {/* Top Header/Title */}
      <header className="bg-gradient-to-r from-blue-400 to-blue-950 text-white py-8 shadow-lg">
        <h1 className="text-5xl font-bold text-center tracking-tight">Fantasy Football Start/Sit Calculator</h1>
        <p className="text-center text-blue-100 mt-2 text-lg">
          Make smarter start/sit decisions with data-driven insights
        </p>
      </header>
      
      {/* Main Content Area with Sidebar */}
      <div className="flex flex-1">
        {/* Left Sidebar */}
        <aside className="w-80 bg-white border-r border-gray-200 p-6 shadow-sm">
          <div className="mb-6">
            <h2 className="text-2xl font-bold text-slate-800 mb-1">Player 1</h2>
            <div className="h-1 w-17 bg-blue-500 rounded"></div>
          </div>
          <div className="bg-gradient-to-br from-blue-50 to-white border-2 border-blue-200 rounded-xl p-5 space-y-3">
            {player1 ? (
              <>
                <div className="border-b border-blue-100 pb-3">
                  <p className="text-2xl font-bold text-blue-900">{player1}</p>
                  <p className="text-sm text-blue-600 font-semibold">{team1} • {position1}</p>
                </div>
                
                <div className="space-y-2 text-sm">
                  <StatRow label="Avg Fantasy Pts" value={avgFP1} highlight />
                  <StatRow label="3-Week Momentum" value={momentum1} />
                  <StatRow label="Avg TD/Game" value={td1} />
                  <StatRow label="Team EPA" value={epa1} />
                  {posStat1 && <p className="text-slate-700 bg-blue-50 p-2 rounded">{posStat1}</p>}
                </div>
              </>
            ) : (
              <p className="text-slate-400 text-center py-8">Select a player to see stats</p>
            )}
          </div>
          <div className="mt-8 mb-6">
            <h2 className="text-2xl font-bold text-slate-800 mb-1">Player 2</h2>
            <div className="h-1 w-17 bg-blue-500 rounded"></div>
          </div>
          
          <div className="bg-gradient-to-br from-blue-50 to-white border-2 border-blue-200 rounded-xl p-5 space-y-3">
            {player2 ? (
              <>
                <div className="border-b border-blue-100 pb-3">
                  <p className="text-2xl font-bold text-blue-900">{player2}</p>
                  <p className="text-sm text-blue-600 font-semibold">{team2} • {position2}</p>
                </div>
                
                <div className="space-y-2 text-sm">
                  <StatRow label="Avg Fantasy Pts" value={avgFP2} highlight />
                  <StatRow label="3-Week Momentum" value={momentum2} />
                  <StatRow label="Avg TD/Game" value={td2} />
                  <StatRow label="Team EPA" value={epa2} />
                  {posStat2 && <p className="text-slate-700 bg-blue-50 p-2 rounded">{posStat2}</p>}
                </div>
              </>
            ) : (
              <p className="text-slate-400 text-center py-8">Select a player to see stats</p>
            )}
          </div>
        </aside>
        
        {/* Main Content */}
        <main className="flex-1 p-8 flex items-center justify-center">
          
          <div className="w-2/3">
            <h2 className="text-3xl font-bold text-slate-800 mb-8 text-center">
              Compare Players
            </h2>
            
            {/* Week Selector */}
            <div className="mb-6">
              <label className="block text-sm font-semibold text-slate-700 mb-2">
                Select Week
              </label>
              <select
                value={week}
                onChange={(e) => setWeek(Number(e.target.value))}
                className="w-full border-2 border-blue-300 rounded-lg px-4 py-3 text-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                {Array.from({ length: 15 }, (_, i) => i + 4).map((w) => (
                  <option key={w} value={w}>Week {w}</option>
                ))}
              </select>
            </div>

            {/* Player Selectors */}
            <div className="space-y-5 mb-8">
              <div>
                <label className="block text-sm font-semibold text-slate-700 mb-2">
                  Player 1
                </label>
                <Select 
                  options={selectPlayers} 
                  value={selectPlayers.find(p => p.value === player1) || null}
                  onChange={(e) => setPlayer1(e ? e.value : '')}
                  placeholder="Search for a player..."
                  isSearchable={true}
                  isClearable={true}
                  styles={selectStyles}
                  className="text-lg"
                />
              </div>

              <div>
                <label className="block text-sm font-semibold text-slate-700 mb-2">
                  Player 2
                </label>
                <Select 
                  options={selectPlayers} 
                  value={selectPlayers.find(p => p.value === player2) || null}
                  onChange={(e) => setPlayer2(e ? e.value : '')}
                  placeholder="Search for a player..."
                  isSearchable={true}
                  isClearable={true}
                  styles={selectStyles}
                  className="text-lg"
                />
              </div>
            </div>

            {/* Submit Button */}
            <button 
              className="w-full bg-gradient-to-r from-blue-400 to-blue-700 text-white text-xl font-bold py-4 rounded-lg hover:from-blue-700 hover:to-blue-800 transition-all shadow-lg hover:shadow-xl transform hover:-translate-y-0.5"
              onClick={submit}
            >
              Analyze Players
            </button>

            {/* Results */}
            {testing && (
              <div className="mt-8 bg-white border-2 border-blue-300 rounded-xl p-8 shadow-lg">
                <div className="text-center">
                  <p className="text-2xl font-bold text-blue-900 mb-2">
                    {testing}
                  </p>
                  <p className="text-xl text-blue-600 font-semibold">
                    {confidence}
                  </p>
                </div>
              </div>
            )}

            {/* Info Note */}
            <div className="mt-8 bg-blue-50 border-l-4 border-blue-500 rounded-lg p-6">
              <p className="text-blue-900 leading-relaxed">
                <span className="font-bold">Note:</span> Due to the football season's conclusion, 
                this application's full ability can't be utilized until the 2026 season starts. 
                Until then feel free to test player stats and model prediction on a week-by-week basis!
              </p>
            </div>
          </div>
          
        </main>
        
        {/* Right Sidebar */}
        <aside className="w-80 bg-white border-l border-gray-200 p-6 shadow-sm">
          <div className="mb-4">
            <h2 className="text-2xl font-bold text-slate-800 mb-1">Top Players 2025</h2>
            <div className="h-1 w-16 bg-blue-500 rounded"></div>
          </div>

          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="w-full border-2 border-blue-300 rounded-lg px-3 py-2 mb-4 focus:outline-none focus:ring-2 focus:ring-blue-500 font-semibold"
          >
            {positions.map((pos) => (
              <option key={pos} value={pos}>{pos}</option>
            ))}
          </select>

          <div className="bg-slate-50 rounded-xl border border-gray-200 overflow-hidden">
            <div className="max-h-[calc(100vh-300px)] overflow-y-auto">
              {players[filter].map((player, index) => (
                <div 
                  key={player.abbreviation}
                  className={`p-3 border-b border-gray-200 hover:bg-blue-50 transition-colors ${
                    index < 3 ? 'bg-blue-50' : ''
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex items-start gap-2">
                      <span className={`font-bold ${
                        index < 3 ? 'text-blue-600 text-lg' : 'text-slate-400'
                      }`}>
                        {index + 1}.
                      </span>
                      <div>
                        <p className="font-bold text-slate-800">{player.abbreviation}</p>
                        <p className="text-xs text-slate-500">{player.team} • {player.position}</p>
                      </div>
                    </div>
                    <p className="font-bold text-blue-600 text-sm">
                      {player.fantasy_points.toFixed(1)}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </aside>
      </div>
    </div>
  );
}
function StatRow({ label, value, highlight = false }) {
  return (
    <div className="flex justify-between items-center">
      <span className="text-slate-600 font-medium">{label}</span>
      <span className={`font-bold ${highlight ? 'text-blue-600 text-lg' : 'text-slate-800'}`}>
        {value}
      </span>
    </div>
  );
}