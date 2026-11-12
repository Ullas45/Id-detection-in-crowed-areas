
import UploadBox from "../components/UploadBox";

import {
  Users,
  Camera,
  Activity
} from "lucide-react";

function Home() {
  return (
    <div className="home-page min-h-screen w-full bg-[#080b12] text-white">

      {/* NAVBAR */}
      <nav className="w-full border-b border-gray-800 bg-[#0b101a]">
        <div className="home-nav-inner max-w-7xl mx-auto px-6 py-5
                        flex justify-between items-center">

          <h1 className="text-2xl font-bold">
            CrowdVision
            <span className="text-blue-500"> AI</span>
          </h1>

          <div className="flex items-center gap-2">
            <span className="w-2 h-2 bg-green-500 rounded-full"></span>
            <span className="text-sm text-gray-400">
              AI System Online
            </span>
          </div>

        </div>
      </nav>

      {/* MAIN CONTENT */}
      <main className="home-main max-w-7xl mx-auto px-6 py-12">

        {/* HERO */}
        <section className="home-hero text-center mb-12">

          <p className="text-blue-400 font-semibold mb-4 tracking-wider">
            AI POWERED CROWD ANALYTICS
          </p>

          <h1 className="text-4xl md:text-6xl font-bold">
            Intelligent Crowd
            <span className="text-blue-500">
              {" "}Detection
            </span>
          </h1>

          <p className="home-hero-description text-gray-400 max-w-2xl mx-auto mt-5 leading-8">
            Detect, count and analyze people in crowded
            images using artificial intelligence and
            computer vision.
          </p>

        </section>

        {/* FEATURE CARDS */}
        <section className="home-feature-grid grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">

          <StatCard
            icon={<Users size={26} />}
            title="Person Detection"
            description="AI-powered person detection in crowded images."
          />

          <StatCard
            icon={<Camera size={26} />}
            title="Image Analysis"
            description="Upload and analyze crowded images."
          />

          <StatCard
            icon={<Activity size={26} />}
            title="Smart Analytics"
            description="Automatic people counting and analysis."
          />

        </section>

        {/* IMAGE DETECTION */}
        <section className="home-upload-section w-full max-w-5xl mx-auto">
          <UploadBox />
        </section>

        {/* FOOTER */}
        <footer className="text-center border-t border-gray-800 mt-12 pt-8">

          <p className="text-gray-400 text-sm">
            CrowdVision AI © 2026
          </p>

          <p className="text-gray-500 text-xs mt-2">
            Intelligent Crowd Detection System
          </p>

        </footer>

      </main>

    </div>
  );
}

function StatCard({ icon, title, description }) {
  return (
    <div className="home-feature-card bg-[#111827] border border-gray-800
                    rounded-xl p-6 hover:border-blue-500
                    transition duration-300">

      <div className="text-blue-400 mb-4">
        {icon}
      </div>

      <h3 className="font-bold text-lg mb-2">
        {title}
      </h3>

      <p className="text-gray-400 text-sm leading-6">
        {description}
      </p>

    </div>
  );
}

export default Home;
