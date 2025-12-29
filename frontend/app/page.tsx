
export default function Home() {
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
          <h2 className="text-xl font-semibold mb-4">Menu</h2>
          <ul className="space-y-2">
            <li>Link 1</li>
            <li>Link 2</li>
            <li>Link 3</li>
          </ul>
        </aside>
        
        {/* Main Content */}
        <main className="flex-1 p-8 text-center">
          <h2 className="text-2xl mb-8">Main Content</h2>
          <div className="p-4">
            <input
              type="text"
              placeholder="Enter player 1 name"
              className="border border-gray-300 rounded px-4 py-2 mr-2"
            />
          </div>
          <div className="p-2">
            <input
              type="text"
              placeholder="Enter player 2 name"
              className="border border-gray-300 rounded px-4 py-2 mr-2"
            />
          </div>
          <button className="bg-blue-500 text-white px-6 py-2 rounded hover:bg-blue-600">
            Submit
          </button>
          
        </main>
        
        {/* Right Sidebar */}
        <aside className="w-64 bg-gray-100 p-6">
          <h2 className="text-xl font-semibold mb-4">Info</h2>
          <p>Additional info here</p>
        </aside>
      </div>
    </div>
  );
}
