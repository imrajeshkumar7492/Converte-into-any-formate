import React from 'react';

const Footer = () => {
  const footerSections = [
    {
      title: "Convert",
      links: [
        "Video Converter",
        "Audio Converter", 
        "Image Converter",
        "Document Converter",
        "Archive Converter"
      ]
    },
    {
      title: "Tools",
      links: [
        "Video Compressor",
        "Image Resizer",
        "PDF Tools",
        "Color Picker",
        "Crop Image"
      ]
    },
    {
      title: "Company",
      links: [
        "About Us",
        "Privacy Policy",
        "Terms of Service", 
        "Security & Compliance",
        "Contact"
      ]
    },
    {
      title: "Support",
      links: [
        "FAQ",
        "API Documentation",
        "Status Page",
        "Donate",
        "Report a Bug"
      ]
    }
  ];

  return (
    <footer className="bg-gray-900 text-white">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-8 mb-8">
          {footerSections.map((section, index) => (
            <div key={index}>
              <h3 className="text-lg font-semibold mb-4">{section.title}</h3>
              <ul className="space-y-2">
                {section.links.map((link, linkIndex) => (
                  <li key={linkIndex}>
                    <a
                      href="#"
                      className="text-gray-400 hover:text-white transition-colors duration-200 text-sm"
                    >
                      {link}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        {/* Logo and Copyright */}
        <div className="border-t border-gray-800 pt-8 flex flex-col sm:flex-row justify-between items-center">
          <div className="flex items-center space-x-2 mb-4 sm:mb-0">
            <div className="w-8 h-8 bg-gradient-to-r from-purple-500 to-blue-500 rounded-full flex items-center justify-center">
              <span className="text-white text-sm font-bold">F</span>
            </div>
            <span className="text-xl font-semibold">FreeConvert</span>
          </div>
          
          <div className="text-center sm:text-right">
            <p className="text-gray-400 text-sm">
              © FreeConvert.com v2.30 All rights reserved (2025)
            </p>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;