import React from 'react';
import { Shield, Server, Lock, Globe, Zap, Users } from 'lucide-react';
import { Button } from './ui/button';
import { securityFeatures } from '../data/mockData';

const FeaturesSection = () => {
  const features = [
    {
      id: 1,
      title: "Convert Any File",
      description: "FreeConvert supports more than 1500 file conversions. You can convert videos, images, audio files, or e-books. There are tons of Advanced Options to fine-tune your conversions.",
      icon: Zap,
      color: "text-blue-500"
    },
    {
      id: 2,
      title: "Works Anywhere", 
      description: "FreeConvert is an online file converter. So it works on Windows, Mac, Linux, or any mobile device. All major browsers are supported. Simply upload a file and select a target format.",
      icon: Globe,
      color: "text-green-500"
    },
    {
      id: 3,
      title: "Privacy Guaranteed",
      description: "We know that file security and privacy are important to you. That is why we use 256-bit SSL encryption when transferring files and automatically delete them after a few hours.",
      icon: Shield,
      color: "text-purple-500"
    }
  ];

  const iconComponents = {
    Shield: Shield,
    Server: Server,
    Lock: Lock
  };

  return (
    <section className="py-20 px-4 sm:px-6 lg:px-8 bg-white">
      <div className="max-w-6xl mx-auto">
        {/* Main Features */}
        <div className="grid md:grid-cols-3 gap-12 mb-20">
          {features.map((feature) => {
            const IconComponent = feature.icon;
            return (
              <div key={feature.id} className="text-center group">
                <div className="flex justify-center mb-6">
                  <div className="w-16 h-16 bg-gradient-to-br from-gray-50 to-gray-100 rounded-full flex items-center justify-center group-hover:from-purple-50 group-hover:to-blue-50 transition-all duration-300">
                    <IconComponent className={`w-8 h-8 ${feature.color}`} />
                  </div>
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-4">{feature.title}</h3>
                <p className="text-gray-600 leading-relaxed">{feature.description}</p>
              </div>
            );
          })}
        </div>

        {/* Security Section */}
        <div className="bg-gradient-to-r from-gray-50 to-blue-50 rounded-2xl p-8 lg:p-12">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              Your Data, Our Priority
            </h2>
            <p className="text-lg text-gray-600 max-w-3xl mx-auto leading-relaxed">
              At FreeConvert, we go beyond just converting files—we protect them. Our robust security framework ensures that your data is always safe, whether you're converting an image, video, or document. With advanced encryption, secure data centers, and vigilant monitoring, we've covered every aspect of your data's safety.
            </p>
            
            <div className="mt-8">
              <Button 
                variant="outline" 
                className="border-purple-200 text-purple-600 hover:bg-purple-50 hover:border-purple-300 transition-all duration-300"
              >
                Learn more about our commitment to security
              </Button>
            </div>
          </div>

          {/* Security Features */}
          <div className="grid md:grid-cols-3 gap-8">
            {securityFeatures.map((feature) => {
              const IconComponent = iconComponents[feature.icon];
              return (
                <div key={feature.id} className="text-center group">
                  <div className="flex justify-center mb-4">
                    <div className="w-12 h-12 bg-white rounded-lg shadow-sm flex items-center justify-center group-hover:shadow-md transition-all duration-300">
                      <IconComponent className="w-6 h-6 text-purple-500" />
                    </div>
                  </div>
                  <h4 className="font-semibold text-gray-900 mb-2">{feature.title}</h4>
                  <p className="text-sm text-gray-600">{feature.description}</p>
                </div>
              );
            })}
          </div>
        </div>

        {/* Upgrade CTA */}
        <div className="bg-gradient-to-r from-purple-500 to-blue-500 rounded-2xl p-8 lg:p-12 mt-16 text-center text-white">
          <h2 className="text-2xl lg:text-3xl font-bold mb-4">
            Want to convert large files without a queue or Ads?
          </h2>
          <p className="text-lg opacity-90 mb-8 max-w-2xl mx-auto">
            Upgrade to our premium plan for faster conversions, larger file support, and an ad-free experience.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button 
              size="lg" 
              className="bg-white text-purple-600 hover:bg-gray-100 font-semibold px-8 py-3 transition-all duration-300 transform hover:scale-105"
            >
              Upgrade Now
            </Button>
            <Button 
              size="lg" 
              variant="outline"
              className="border-white text-white hover:bg-white hover:text-purple-600 font-semibold px-8 py-3 transition-all duration-300"
            >
              Sign Up
            </Button>
          </div>
        </div>
      </div>
    </section>
  );
};

export default FeaturesSection;