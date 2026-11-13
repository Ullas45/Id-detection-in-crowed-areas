import {
  Activity,
  ArrowDown,
  ArrowRight,
  ScanFace,
  ShieldCheck,
  Sparkles,
  Users
} from "lucide-react";
import UploadBox from "../components/UploadBox";
import crowdScanVisual from "../assets/crowd-scan.svg";

const highlights = [
  {
    icon: Users,
    title: "Crowd intelligence",
    description: "Find and count people in busy scenes."
  },
  {
    icon: ScanFace,
    title: "Person matching",
    description: "Look for one person across a photo or video."
  },
  {
    icon: Activity,
    title: "Video analytics",
    description: "See detection results throughout the clip."
  }
];

function Home() {
  return (
    <div className="home-page">
      <nav className="site-nav">
        <a className="brand-lockup" href="#top" aria-label="CrowdVision AI home">
          <span className="brand-mark">
            <ScanFace size={21} strokeWidth={2.2} />
          </span>
          <span className="brand-name">
            CrowdVision<span>AI</span>
          </span>
        </a>

        <div className="nav-actions">
          <a className="nav-link" href="#capabilities">Capabilities</a>
          <a className="nav-cta" href="#workspace">
            Open workspace <ArrowRight size={15} />
          </a>
          <div className="service-status">
            <span className="status-dot" />
            AI online
          </div>
        </div>
      </nav>

      <main id="top">
        <section className="hero-section">
          <div className="hero-copy">
            <div className="eyebrow">
              <Sparkles size={14} />
              <span>AI-POWERED CROWD ANALYTICS</span>
            </div>

            <h1>
              Every face.
              <br />
              <span>In focus.</span>
            </h1>

            <p className="hero-description">
              Turn images and video into clear, actionable crowd insights.
              Count everyone—or find the person you’re looking for.
            </p>

            <div className="hero-actions">
              <a className="primary-link" href="#workspace">
                Start detecting <ArrowRight size={17} />
              </a>
              <a className="secondary-link" href="#capabilities">
                Explore capabilities <ArrowDown size={16} />
              </a>
            </div>

            <div className="hero-trust">
              <ShieldCheck size={17} />
              <span>Your media stays on your server</span>
            </div>
          </div>

          <div className="hero-visual">
            <div className="visual-glow" />
            <div className="visual-frame">
              <img
                src={crowdScanVisual}
                alt="Illustrated crowd with person-detection boxes"
              />
              <div className="visual-caption">
                <span className="caption-pulse" />
                <span>VISION SYSTEM</span>
                <span className="caption-live">READY</span>
              </div>
              <div className="visual-crosshair visual-crosshair-top" />
              <div className="visual-crosshair visual-crosshair-bottom" />
            </div>
            <div className="floating-chip">
              <span className="chip-icon"><Activity size={17} /></span>
              <span>
                <strong>Smart analysis</strong>
                <small>Images · Video · People</small>
              </span>
            </div>
            <div className="visual-index">01 <span>/</span> VISION</div>
          </div>
        </section>

        <section className="capabilities-section" id="capabilities">
          <div className="section-heading">
            <div>
              <p className="section-kicker">BUILT FOR THE BIG PICTURE</p>
              <h2>One platform. Clearer perspective.</h2>
            </div>
            <p className="section-aside">
              Powerful vision tools, made refreshingly simple to use.
            </p>
          </div>

          <div className="capability-grid">
            {highlights.map(({ icon: Icon, title, description }, index) => (
              <article className="capability-card" key={title}>
                <span className="capability-number">0{index + 1}</span>
                <span className="capability-icon"><Icon size={20} /></span>
                <h3>{title}</h3>
                <p>{description}</p>
                <span className="capability-rule" />
              </article>
            ))}
          </div>
        </section>

        <section className="workspace-section" id="workspace">
          <div className="workspace-heading">
            <div>
              <p className="section-kicker">YOUR ANALYSIS STUDIO</p>
              <h2>Let’s take a closer look.</h2>
              <p>Choose an analysis mode and add your media to get started.</p>
            </div>
            <span className="workspace-badge">
              <span className="status-dot" />
              PRIVATE WORKSPACE
            </span>
          </div>
          <UploadBox />
        </section>
      </main>

      <footer className="site-footer">
        <a className="brand-lockup footer-brand" href="#top">
          <span className="brand-mark">
            <ScanFace size={18} strokeWidth={2.2} />
          </span>
          <span className="brand-name">CrowdVision<span>AI</span></span>
        </a>
        <p>See the people. Understand the picture.</p>
        <span className="footer-copyright">© 2026 CrowdVision AI</span>
      </footer>
    </div>
  );
}

export default Home;
