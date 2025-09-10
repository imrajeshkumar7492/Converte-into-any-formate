import React from 'react';
import { 
  Zap, 
  Shield, 
  Clock, 
  Download, 
  Settings, 
  FileText, 
  Image, 
  Video, 
  Music,
  Archive,
  CheckCircle,
  Star
} from 'lucide-react';

const AdvancedFeatures = () => {
  const features = [
    {
      icon: <Zap className="w-8 h-8 text-blue-600" />,
      title: "Lightning Fast Conversion",
      description: "Convert files in seconds with our optimized processing engine",
      highlight: "10x faster than competitors"
    },
    {
      icon: <Shield className="w-8 h-8 text-green-600" />,
      title: "Secure & Private",
      description: "Your files are processed securely and deleted immediately after conversion",
      highlight: "100% secure"
    },
    {
      icon: <Settings className="w-8 h-8 text-purple-600" />,
      title: "Advanced Options",
      description: "Customize quality, resolution, and compression settings for optimal results",
      highlight: "Professional grade"
    },
    {
      icon: <Download className="w-8 h-8 text-orange-600" />,
      title: "Batch Processing",
      description: "Convert multiple files simultaneously with different format options",
      highlight: "Save time"
    },
    {
      icon: <FileText className="w-8 h-8 text-indigo-600" />,
      title: "Format Preservation",
      description: "Maintain formatting, styles, and quality across all document conversions",
      highlight: "Perfect fidelity"
    },
    {
      icon: <Clock className="w-8 h-8 text-red-600" />,
      title: "Real-time Progress",
      description: "Track conversion progress with detailed status updates and ETA",
      highlight: "Always informed"
    }
  ];

  const formatCategories = [
    {
      icon: <Image className="w-6 h-6" />,
      name: "Images",
      formats: ["JPG", "PNG", "WEBP", "TIFF", "BMP", "GIF", "SVG", "ICO"],
      count: "8+ formats"
    },
    {
      icon: <FileText className="w-6 h-6" />,
      name: "Documents",
      formats: ["PDF", "DOC", "DOCX", "TXT", "RTF", "ODT", "EPUB", "MOBI"],
      count: "8+ formats"
    },
    {
      icon: <Video className="w-6 h-6" />,
      name: "Videos",
      formats: ["MP4", "AVI", "MOV", "WMV", "FLV", "MKV", "WEBM", "OGV"],
      count: "8+ formats"
    },
    {
      icon: <Music className="w-6 h-6" />,
      name: "Audio",
      formats: ["MP3", "WAV", "FLAC", "AAC", "OGG", "M4A", "WMA", "AIFF"],
      count: "8+ formats"
    },
    {
      icon: <Archive className="w-6 h-6" />,
      name: "Archives",
      formats: ["ZIP", "RAR", "7Z", "TAR", "GZ", "BZ2"],
      count: "6+ formats"
    }
  ];

  return (
    <section className="py-20 px-4 sm:px-6 lg:px-8 bg-white">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold text-gray-900 mb-4">
            Professional-Grade File Conversion
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Experience the most advanced file conversion platform with enterprise-level features, 
            lightning-fast processing, and perfect format preservation.
          </p>
        </div>

        {/* Advanced Features Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8 mb-20">
          {features.map((feature, index) => (
            <div 
              key={index}
              className="group relative bg-white rounded-2xl p-8 shadow-lg hover:shadow-xl transition-all duration-300 border border-gray-100 hover:border-blue-200"
            >
              <div className="flex items-start space-x-4">
                <div className="flex-shrink-0">
                  {feature.icon}
                </div>
                <div className="flex-1">
                  <h3 className="text-xl font-semibold text-gray-900 mb-2 group-hover:text-blue-600 transition-colors">
                    {feature.title}
                  </h3>
                  <p className="text-gray-600 mb-3">
                    {feature.description}
                  </p>
                  <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800">
                    <Star className="w-4 h-4 mr-1" />
                    {feature.highlight}
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Format Support */}
        <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-3xl p-12">
          <div className="text-center mb-12">
            <h3 className="text-3xl font-bold text-gray-900 mb-4">
              Comprehensive Format Support
            </h3>
            <p className="text-lg text-gray-600">
              Convert between 40+ file formats across all major categories
            </p>
          </div>

          <div className="grid sm:grid-cols-2 lg:grid-cols-5 gap-6">
            {formatCategories.map((category, index) => (
              <div 
                key={index}
                className="bg-white rounded-xl p-6 shadow-sm hover:shadow-md transition-all duration-300 group"
              >
                <div className="flex items-center space-x-3 mb-4">
                  <div className="text-blue-600 group-hover:scale-110 transition-transform">
                    {category.icon}
                  </div>
                  <div>
                    <h4 className="font-semibold text-gray-900">{category.name}</h4>
                    <p className="text-sm text-blue-600 font-medium">{category.count}</p>
                  </div>
                </div>
                <div className="flex flex-wrap gap-1">
                  {category.formats.map((format, formatIndex) => (
                    <span 
                      key={formatIndex}
                      className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded-md font-mono"
                    >
                      {format}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Stats */}
        <div className="mt-20 grid grid-cols-2 md:grid-cols-4 gap-8">
          <div className="text-center">
            <div className="text-4xl font-bold text-blue-600 mb-2">40+</div>
            <div className="text-gray-600">Supported Formats</div>
          </div>
          <div className="text-center">
            <div className="text-4xl font-bold text-green-600 mb-2">99.9%</div>
            <div className="text-gray-600">Uptime</div>
          </div>
          <div className="text-center">
            <div className="text-4xl font-bold text-purple-600 mb-2">1M+</div>
            <div className="text-gray-600">Files Converted</div>
          </div>
          <div className="text-center">
            <div className="text-4xl font-bold text-orange-600 mb-2">10x</div>
            <div className="text-gray-600">Faster Processing</div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default AdvancedFeatures;