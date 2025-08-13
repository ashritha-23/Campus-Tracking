
import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Users, MapPin, Clock, Camera } from "lucide-react";
import StatsCard from './StatsCard';

const Overview = () => {
  // Mock data for the dashboard
  const stats = [
    {
      title: "Total Students",
      value: "1,284",
      icon: <Users className="h-4 w-4 text-blue-600" />,
      description: "tracked in the system"
    },
    {
      title: "Active Locations",
      value: "4",
      icon: <MapPin className="h-4 w-4 text-green-600" />,
      description: "Library, Canteen, Classroom, Lab"
    },
    {
      title: "Today's Records",
      value: "347",
      icon: <Clock className="h-4 w-4 text-amber-600" />,
      description: "student appearances logged"
    },
    {
      title: "Active Cameras",
      value: "6",
      icon: <Camera className="h-4 w-4 text-purple-600" />,
      description: "monitoring campus locations"
    }
  ];

  return (
    <div className="space-y-6">
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat, index) => (
          <StatsCard key={index} {...stat} />
        ))}
      </div>
      
      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Current Activity</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-80 bg-gray-100 rounded-md flex items-center justify-center">
              <p className="text-gray-500">Activity chart will appear here</p>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader>
            <CardTitle>Location Distribution</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <div className="flex items-center">
                  <div className="w-3 h-3 rounded-full bg-blue-500 mr-2"></div>
                  <span>Library</span>
                </div>
                <span className="font-medium">42%</span>
              </div>
              <div className="h-2 bg-gray-200 rounded">
                <div className="h-full bg-blue-500 rounded" style={{ width: '42%' }}></div>
              </div>
              
              <div className="flex justify-between items-center">
                <div className="flex items-center">
                  <div className="w-3 h-3 rounded-full bg-green-500 mr-2"></div>
                  <span>Classroom</span>
                </div>
                <span className="font-medium">28%</span>
              </div>
              <div className="h-2 bg-gray-200 rounded">
                <div className="h-full bg-green-500 rounded" style={{ width: '28%' }}></div>
              </div>
              
              <div className="flex justify-between items-center">
                <div className="flex items-center">
                  <div className="w-3 h-3 rounded-full bg-amber-500 mr-2"></div>
                  <span>Canteen</span>
                </div>
                <span className="font-medium">18%</span>
              </div>
              <div className="h-2 bg-gray-200 rounded">
                <div className="h-full bg-amber-500 rounded" style={{ width: '18%' }}></div>
              </div>
              
              <div className="flex justify-between items-center">
                <div className="flex items-center">
                  <div className="w-3 h-3 rounded-full bg-purple-500 mr-2"></div>
                  <span>Lab</span>
                </div>
                <span className="font-medium">12%</span>
              </div>
              <div className="h-2 bg-gray-200 rounded">
                <div className="h-full bg-purple-500 rounded" style={{ width: '12%' }}></div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Overview;
