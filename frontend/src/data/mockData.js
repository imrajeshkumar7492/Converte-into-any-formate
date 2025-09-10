// Mock data for FreeConvert clone
export const popularConverters = [
  {
    id: 1,
    category: "Video Converter",
    converters: [
      { name: "MP4 Converter", url: "/mp4-converter" },
      { name: "Video to GIF", url: "/convert/video-to-gif" },
      { name: "MOV to MP4", url: "/mov-to-mp4" },
      { name: "Video Converter", url: "/video-converter" }
    ]
  },
  {
    id: 2,
    category: "Audio Converter", 
    converters: [
      { name: "MP3 Converter", url: "/mp3-converter" },
      { name: "MP4 to MP3", url: "/mp4-to-mp3" },
      { name: "Video to MP3", url: "/convert/video-to-mp3" },
      { name: "Audio Converter", url: "/audio-converter" }
    ]
  },
  {
    id: 3,
    category: "Image Converter",
    converters: [
      { name: "JPG to PDF", url: "/jpg-to-pdf" },
      { name: "PDF to JPG", url: "/pdf-to-jpg" },
      { name: "HEIC to JPG", url: "/heic-to-jpg" },
      { name: "Image to PDF", url: "/convert/image-to-pdf" },
      { name: "Image Converter", url: "/image-converter" }
    ]
  },
  {
    id: 4,
    category: "Document & Ebook",
    converters: [
      { name: "PDF to WORD", url: "/pdf-to-word" },
      { name: "EPUB to PDF", url: "/epub-to-pdf" },
      { name: "EPUB to MOBI", url: "/epub-to-mobi" },
      { name: "Document Converter", url: "/document-converter" }
    ]
  },
  {
    id: 5,
    category: "Archive & Time",
    converters: [
      { name: "RAR to Zip", url: "/rar-to-zip" },
      { name: "PST to EST", url: "/time/pst-to-est" },
      { name: "CST to EST", url: "/time/cst-to-est" },
      { name: "Archive Converter", url: "/archive-converter" }
    ]
  },
  {
    id: 6,
    category: "Unit Converter",
    converters: [
      { name: "Lbs to Kg", url: "/unit/lbs-to-kg" },
      { name: "Kg to Lbs", url: "/unit/kg-to-lbs" },
      { name: "Feet to Meters", url: "/unit/feet-to-meters" },
      { name: "Unit Converter", url: "/unit-converter" }
    ]
  },
  {
    id: 7,
    category: "Web Apps",
    converters: [
      { name: "Collage Maker", url: "/collage-maker" },
      { name: "Image Resizer", url: "/image-resizer" },
      { name: "Crop Image", url: "/crop-image" },
      { name: "Color Picker", url: "/color-picker" }
    ]
  },
  {
    id: 8,
    category: "Mobile Apps",
    converters: [
      { name: "Collage Maker Android", url: "#" },
      { name: "Collage Maker iOS", url: "#" },
      { name: "Image Converter Android", url: "#" },
      { name: "Image Converter iOS", url: "#" }
    ]
  }
];

export const securityFeatures = [
  {
    id: 1,
    title: "SSL/TLS Encryption",
    description: "256-bit SSL encryption when transferring files",
    icon: "Shield"
  },
  {
    id: 2,
    title: "Secured Data Centers", 
    description: "Advanced security in our data centers",
    icon: "Server"
  },
  {
    id: 3,
    title: "Access Control and Authentication",
    description: "Vigilant monitoring and access control",
    icon: "Lock"
  }
];

export const navItems = [
  {
    name: "Convert",
    hasDropdown: true,
    items: ["Video Converter", "Audio Converter", "Image Converter", "Document Converter"]
  },
  {
    name: "Compress", 
    hasDropdown: true,
    items: ["Video Compressor", "Image Compressor", "PDF Compressor"]
  },
  {
    name: "Tools",
    hasDropdown: true,
    items: ["Video Editor", "Image Editor", "PDF Tools"]
  },
  {
    name: "API",
    hasDropdown: false,
    url: "/api"
  },
  {
    name: "Pricing",
    hasDropdown: false,
    url: "/pricing"
  }
];

// Mock conversion process
export const mockConversionProcess = {
  steps: [
    "Uploading file...",
    "Processing conversion...", 
    "Optimizing output...",
    "Finalizing...",
    "Complete!"
  ],
  duration: 3000 // 3 seconds for demo
};