import React from "react";
import "./HomePage.css";
import logo from "./logo.png";

function HomePage() {
  return (
    <div className="container">
      {/* Header */}
      <header className="navbar">
        <img src={logo} alt="BotCraft Logo" className="logo" />
        <nav className="nav-links">
          <a href="#about">About</a>
          <a href="#pricing">Pricing</a>
          <a href="#guidelines">Guidelines</a>
          <a href="#faqs">FAQs</a>
        </nav>
        <div className="auth-buttons">
          <button className="login-btn">Log In</button>
          <button className="signup-btn">Sign Up</button>
        </div>
      </header>

      {/* Hero Section */}
      <section className="hero">
        <h1>
          <span className="highlight">BotCraft:</span>
          <br /> Transform Websites and Documents into Custom Chatbots
        </h1>
      </section>

      {/* About Section */}
      <section id="about" className="about-section">
        <p>
          Welcome to <b>BotCraft</b>, your trusted platform for creating
          intelligent, bilingual chatbots tailored to your unique needs. At
          BotCraft, we offer two innovative services designed to empower
          students, teachers, and businesses:
        </p>

        {/* For Students and Teachers */}
        <div className="card">
          <h2>1. For Students and Teachers:</h2>
          <p>
            Take your learning experience to the next level with personalized
            chatbots. Simply upload your PDFs – be it textbooks, lecture notes,
            or study guides – and transform them into an interactive chatbot.
            Our platform makes studying smarter, helping you quickly find
            answers and understand your content.
          </p>
        </div>

        {/* For Businesses */}
        <div className="card">
          <h2>2. For Businesses:</h2>
          <p>
            Enhance your customer service with a chatbot designed specifically
            for your website. Simply provide your website URL, and we’ll create
            a customized chatbot that integrates seamlessly with your site,
            helping you provide instant support, answer FAQs, or engage
            customers more efficiently.
          </p>
        </div>

        {/* Ending Note */}
        <p>
          Our chatbots are bilingual, supporting both <b>English and Urdu</b>,
          ensuring accessibility for a wider audience. Whether you're a student,
          teacher, or business owner, BotCraft offers a user-friendly AI
          solution to meet your needs.
        </p>
        <button className="cta-btn">Join BotCraft Today</button>
      </section>
    </div>
  );
}

export default HomePage;
