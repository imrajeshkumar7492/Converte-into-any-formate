import React from 'react';
import { ArrowRight } from 'lucide-react';
import { popularConverters } from '../data/mockData';

const PopularConverters = () => {
  return (
    <section className="py-20 px-4 sm:px-6 lg:px-8 bg-gray-50">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-16">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">
            Popular Converters
          </h2>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Choose from our most popular conversion tools, covering everything from media files to documents and units.
          </p>
        </div>

        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-8">
          {popularConverters.map((category) => (
            <div 
              key={category.id} 
              className="bg-white rounded-xl p-6 shadow-sm hover:shadow-md transition-all duration-300 group border border-gray-100"
            >
              <h3 className="text-lg font-semibold text-gray-900 mb-4 group-hover:text-purple-600 transition-colors duration-300">
                {category.category}
              </h3>
              
              <ul className="space-y-3">
                {category.converters.map((converter, index) => (
                  <li key={index}>
                    <a
                      href={converter.url}
                      className="flex items-center justify-between text-gray-600 hover:text-purple-600 transition-colors duration-200 group/item"
                    >
                      <span className="text-sm">{converter.name}</span>
                      <ArrowRight className="w-4 h-4 opacity-0 group-hover/item:opacity-100 transform translate-x-1 group-hover/item:translate-x-0 transition-all duration-200" />
                    </a>
                  </li>
                ))}
              </ul>
              
              {category.converters.length > 4 && (
                <div className="mt-4 pt-4 border-t border-gray-100">
                  <a
                    href="#"
                    className="text-sm text-purple-500 hover:text-purple-600 font-medium flex items-center group/more"
                  >
                    View all
                    <ArrowRight className="w-4 h-4 ml-1 transform group-hover/more:translate-x-1 transition-transform duration-200" />
                  </a>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default PopularConverters;