import { Bars3Icon } from '@heroicons/react/24/solid';
import { useState } from 'react';

function Navbar() {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isDashboardHovered, setIsDashboardHovered] = useState(false);
  const [isChatbotHovered, setIsChatbotHovered] = useState(false);
  const [isTimeHovered, setIsTimeHovered] = useState(false);
  const [isContatoHovered, setIsContatoHovered] = useState(false);

  const toggleMenu = () => {
    setIsMenuOpen(!isMenuOpen);
  };

  return (
    <nav className="bg-gray-100 py-4 border-b-2 border-black">
      <div className="max-w-7xl mx-auto px-4 flex justify-between items-center">
        <div className="flex items-center">
          <img src="pinguim.png" alt="Logo" className="h-8" />
          <span className="ml-2 text-black text-lg">Gurizada</span>
        </div>
        <button onClick={toggleMenu} className="block md:hidden text-white">
          <Bars3Icon className='h-8 text-black'/>
        </button>
        {isMenuOpen && (
          <div className="fixed inset-y-0 left-0 z-40 bg-gray-100 text-black p-4">
            <a href="dashboard" className="block w-full py-2 px-2 mb-2 ">Dashboard</a>
            <a href="chatbot" className="block w-full py-2 px-2 mb-2 ">Chatbot</a>
            <a href="time" className="block w-full py-2 px-2 mb-2 ">Time</a>
            <a href="contato" className="block w-full py-2 px-2 mb-2 ">Contato</a>
          </div>
        )}
        <div className="hidden md:flex flex-grow justify-end">
          <a
            href="dashboard"
            className="relative inline-block text-black px-3 py-2"
            onMouseEnter={() => setIsDashboardHovered(true)}
            onMouseLeave={() => setIsDashboardHovered(false)}
          >
            Dashboard
            {isDashboardHovered && <span className="absolute bottom-0 left-0 w-full h-0.5 bg-green-500 transition-all line-animation"></span>}
          </a>
          <a
            href="chatbot"
            className="relative inline-block text-black px-3 py-2"
            onMouseEnter={() => setIsChatbotHovered(true)}
            onMouseLeave={() => setIsChatbotHovered(false)}
          >
            Chatbot
            {isChatbotHovered && <span className="absolute bottom-0 left-0 w-full h-0.5 bg-green-500 transition-all line-animation"></span>}
          </a>
          <a
            href="time"
            className="relative inline-block text-black px-3 py-2"
            onMouseEnter={() => setIsTimeHovered(true)}
            onMouseLeave={() => setIsTimeHovered(false)}
          >
            Time
            {isTimeHovered && <span className="absolute bottom-0 left-0 w-full h-0.5 bg-green-500 transition-all line-animation"></span>}
          </a>
          <a
            href="contato"
            className="relative inline-block text-black px-3 py-2"
            onMouseEnter={() => setIsContatoHovered(true)}
            onMouseLeave={() => setIsContatoHovered(false)}
          >
            Contato
            {isContatoHovered && <span className="absolute bottom-0 left-0 w-full h-0.5 bg-green-500 transition-all line-animation"></span>}
          </a>
        </div>
      </div>
    </nav>
  );
}

export default Navbar;
