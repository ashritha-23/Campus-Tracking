
import React, { useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Camera, Library, Coffee, User } from "lucide-react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Switch } from "@/components/ui/switch";
import { useToast } from "@/components/ui/use-toast";

// Mock camera data
const mockCameras = [
  { id: 'cam1', name: 'Library Main', location: 'Library', status: true },
  { id: 'cam2', name: 'Library Study Area', location: 'Library', status: true },
  { id: 'cam3', name: 'Canteen Entrance', location: 'Canteen', status: true },
  { id: 'cam4', name: 'Canteen Seating', location: 'Canteen', status: false },
  { id: 'cam5', name: 'Classroom 101', location: 'Classroom', status: true },
  { id: 'cam6', name: 'Lab Room', location: 'Lab', status: true },
];

const CameraControl = () => {
  const [cameras, setCameras] = useState(mockCameras);
  const [newCamera, setNewCamera] = useState({ name: '', location: 'Library', url: '' });
  const { toast } = useToast();

  const handleCameraToggle = (id: string) => {
    setCameras(cameras.map(camera => 
      camera.id === id ? { ...camera, status: !camera.status } : camera
    ));
    
    const camera = cameras.find(c => c.id === id);
    
    toast({
      title: camera?.status ? "Camera Deactivated" : "Camera Activated",
      description: `${camera?.name} is now ${camera?.status ? "inactive" : "active"}.`,
    });
  };

  const handleAddCamera = (e: React.FormEvent) => {
    e.preventDefault();
    if (newCamera.name && newCamera.url) {
      const id = `cam${cameras.length + 1}`;
      setCameras([...cameras, { id, name: newCamera.name, location: newCamera.location, status: true }]);
      setNewCamera({ name: '', location: 'Library', url: '' });
      
      toast({
        title: "Camera Added",
        description: `${newCamera.name} has been added to the system.`,
      });
    }
  };

  return (
    <div className="space-y-6">
      <div className="grid md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Camera Management</CardTitle>
            <CardDescription>Control cameras in different locations</CardDescription>
          </CardHeader>
          <CardContent>
            <Tabs defaultValue="all">
              <TabsList className="grid grid-cols-5">
                <TabsTrigger value="all">All</TabsTrigger>
                <TabsTrigger value="library">Library</TabsTrigger>
                <TabsTrigger value="canteen">Canteen</TabsTrigger>
                <TabsTrigger value="classroom">Class</TabsTrigger>
                <TabsTrigger value="lab">Lab</TabsTrigger>
              </TabsList>
              
              <TabsContent value="all" className="mt-4 space-y-4">
                {cameras.map((camera) => (
                  <div key={camera.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-md">
                    <div className="flex items-center">
                      <Camera className="h-5 w-5 mr-3 text-gray-500" />
                      <div>
                        <p className="font-medium">{camera.name}</p>
                        <p className="text-sm text-muted-foreground">{camera.location}</p>
                      </div>
                    </div>
                    <Switch
                      checked={camera.status}
                      onCheckedChange={() => handleCameraToggle(camera.id)}
                    />
                  </div>
                ))}
              </TabsContent>
              
              <TabsContent value="library" className="mt-4 space-y-4">
                {cameras
                  .filter(camera => camera.location === 'Library')
                  .map((camera) => (
                    <div key={camera.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-md">
                      <div className="flex items-center">
                        <Library className="h-5 w-5 mr-3 text-blue-600" />
                        <p className="font-medium">{camera.name}</p>
                      </div>
                      <Switch
                        checked={camera.status}
                        onCheckedChange={() => handleCameraToggle(camera.id)}
                      />
                    </div>
                  ))}
              </TabsContent>
              
              <TabsContent value="canteen" className="mt-4 space-y-4">
                {cameras
                  .filter(camera => camera.location === 'Canteen')
                  .map((camera) => (
                    <div key={camera.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-md">
                      <div className="flex items-center">
                        <Coffee className="h-5 w-5 mr-3 text-amber-600" />
                        <p className="font-medium">{camera.name}</p>
                      </div>
                      <Switch
                        checked={camera.status}
                        onCheckedChange={() => handleCameraToggle(camera.id)}
                      />
                    </div>
                  ))}
              </TabsContent>
              
              <TabsContent value="classroom" className="mt-4 space-y-4">
                {cameras
                  .filter(camera => camera.location === 'Classroom')
                  .map((camera) => (
                    <div key={camera.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-md">
                      <div className="flex items-center">
                        <User className="h-5 w-5 mr-3 text-green-600" />
                        <p className="font-medium">{camera.name}</p>
                      </div>
                      <Switch
                        checked={camera.status}
                        onCheckedChange={() => handleCameraToggle(camera.id)}
                      />
                    </div>
                  ))}
              </TabsContent>
              
              <TabsContent value="lab" className="mt-4 space-y-4">
                {cameras
                  .filter(camera => camera.location === 'Lab')
                  .map((camera) => (
                    <div key={camera.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-md">
                      <div className="flex items-center">
                        <User className="h-5 w-5 mr-3 text-purple-600" />
                        <p className="font-medium">{camera.name}</p>
                      </div>
                      <Switch
                        checked={camera.status}
                        onCheckedChange={() => handleCameraToggle(camera.id)}
                      />
                    </div>
                  ))}
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Add New Camera</CardTitle>
            <CardDescription>Configure a new camera for tracking</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleAddCamera} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="camera-name">Camera Name</Label>
                <Input 
                  id="camera-name" 
                  placeholder="Enter camera name" 
                  value={newCamera.name}
                  onChange={(e) => setNewCamera({...newCamera, name: e.target.value})}
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="camera-location">Location</Label>
                <select 
                  id="camera-location" 
                  className="w-full p-2 border rounded-md"
                  value={newCamera.location}
                  onChange={(e) => setNewCamera({...newCamera, location: e.target.value})}
                >
                  <option value="Library">Library</option>
                  <option value="Canteen">Canteen</option>
                  <option value="Classroom">Classroom</option>
                  <option value="Lab">Lab</option>
                </select>
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="camera-url">Camera URL/IP</Label>
                <Input 
                  id="camera-url" 
                  placeholder="rtsp:// or http://" 
                  value={newCamera.url}
                  onChange={(e) => setNewCamera({...newCamera, url: e.target.value})}
                />
              </div>
              
              <Button type="submit" className="w-full">Add Camera</Button>
            </form>
            
            <div className="mt-6">
              <h3 className="text-sm font-medium mb-2">Integration Help</h3>
              <p className="text-sm text-muted-foreground">
                To connect your Python face recognition system, ensure that your Flask backend is running and accessible from this interface. Set up your camera URLs correctly for the best recognition results.
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
      
      <Card>
        <CardHeader>
          <CardTitle>Camera Preview</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {cameras
              .filter(camera => camera.status)
              .slice(0, 3)
              .map((camera) => (
                <div key={camera.id} className="bg-gray-100 h-48 rounded-md relative">
                  <div className="absolute top-2 left-2 p-1 px-2 bg-white text-xs rounded shadow-sm">
                    {camera.name}
                  </div>
                  <div className="w-full h-full flex items-center justify-center">
                    <Camera className="h-8 w-8 text-gray-400" />
                  </div>
                </div>
              ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default CameraControl;
