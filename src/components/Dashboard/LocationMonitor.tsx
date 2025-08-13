
import React, { useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Library, Coffee, User } from "lucide-react";

// Mock student data
const mockStudentData = {
  library: [
    { id: 'S001', name: 'John Smith', time: '09:15 AM', avatar: '' },
    { id: 'S012', name: 'Emily Johnson', time: '09:22 AM', avatar: '' },
    { id: 'S045', name: 'Michael Brown', time: '09:30 AM', avatar: '' },
    { id: 'S067', name: 'Sarah Davis', time: '09:45 AM', avatar: '' },
    { id: 'S089', name: 'David Wilson', time: '10:05 AM', avatar: '' },
  ],
  canteen: [
    { id: 'S023', name: 'Jessica Taylor', time: '12:10 PM', avatar: '' },
    { id: 'S056', name: 'Daniel Martinez', time: '12:15 PM', avatar: '' },
    { id: 'S078', name: 'Sophia Anderson', time: '12:25 PM', avatar: '' },
  ],
  classroom: [
    { id: 'S034', name: 'Matthew Thomas', time: '11:00 AM', avatar: '' },
    { id: 'S045', name: 'Michael Brown', time: '11:00 AM', avatar: '' },
    { id: 'S089', name: 'David Wilson', time: '11:05 AM', avatar: '' },
    { id: 'S012', name: 'Emily Johnson', time: '11:10 AM', avatar: '' },
  ],
  lab: [
    { id: 'S067', name: 'Sarah Davis', time: '02:15 PM', avatar: '' },
    { id: 'S078', name: 'Sophia Anderson', time: '02:20 PM', avatar: '' },
  ]
};

const LocationCard = ({ title, icon, count, color }: { title: string, icon: React.ReactNode, count: number, color: string }) => (
  <Card className={`border-l-4 ${color}`}>
    <CardContent className="pt-6">
      <div className="flex justify-between items-center">
        <div>
          <p className="text-sm text-muted-foreground">{title}</p>
          <h3 className="text-2xl font-bold">{count} students</h3>
        </div>
        <div className={`p-2 rounded-full ${color.replace('border-', 'bg-').replace('-600', '-100')}`}>
          {icon}
        </div>
      </div>
    </CardContent>
  </Card>
);

const StudentList = ({ students }: { students: Array<{ id: string, name: string, time: string, avatar: string }> }) => (
  <ScrollArea className="h-[400px] pr-4">
    {students.map((student) => (
      <div key={student.id} className="flex items-center p-3 hover:bg-gray-50 rounded-md">
        <Avatar className="h-10 w-10">
          <AvatarImage src={student.avatar} alt={student.name} />
          <AvatarFallback>{student.name.charAt(0)}</AvatarFallback>
        </Avatar>
        <div className="ml-4 space-y-1">
          <p className="text-sm font-medium leading-none">{student.name}</p>
          <p className="text-sm text-muted-foreground">{student.id}</p>
        </div>
        <div className="ml-auto text-sm text-muted-foreground">
          {student.time}
        </div>
      </div>
    ))}
  </ScrollArea>
);

const LocationMonitor = () => {
  const [selectedLocation, setSelectedLocation] = useState('library');
  
  const locationIcons = {
    library: <Library className="h-6 w-6 text-blue-600" />,
    canteen: <Coffee className="h-6 w-6 text-amber-600" />,
    classroom: <User className="h-6 w-6 text-green-600" />,
    lab: <User className="h-6 w-6 text-purple-600" />
  };

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <LocationCard 
          title="Library" 
          icon={locationIcons.library} 
          count={mockStudentData.library.length} 
          color="border-blue-600" 
        />
        <LocationCard 
          title="Canteen" 
          icon={locationIcons.canteen} 
          count={mockStudentData.canteen.length} 
          color="border-amber-600" 
        />
        <LocationCard 
          title="Classroom" 
          icon={locationIcons.classroom} 
          count={mockStudentData.classroom.length} 
          color="border-green-600" 
        />
        <LocationCard 
          title="Lab" 
          icon={locationIcons.lab} 
          count={mockStudentData.lab.length} 
          color="border-purple-600" 
        />
      </div>
      
      <Card>
        <CardHeader>
          <CardTitle>Location Monitoring</CardTitle>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue="library" onValueChange={setSelectedLocation}>
            <TabsList className="grid grid-cols-4 mb-4">
              <TabsTrigger value="library">Library</TabsTrigger>
              <TabsTrigger value="canteen">Canteen</TabsTrigger>
              <TabsTrigger value="classroom">Classroom</TabsTrigger>
              <TabsTrigger value="lab">Lab</TabsTrigger>
            </TabsList>
            
            <div className="relative h-80 bg-gray-100 rounded-md mb-4">
              <div className="absolute top-2 left-2 p-2 bg-white rounded-md shadow-sm">
                {selectedLocation.charAt(0).toUpperCase() + selectedLocation.slice(1)} Camera Feed
              </div>
              <div className="w-full h-full flex items-center justify-center">
                <p className="text-gray-500">Camera feed will appear here</p>
              </div>
            </div>
            
            <TabsContent value="library">
              <h3 className="mb-4 font-medium">Students in Library</h3>
              <StudentList students={mockStudentData.library} />
            </TabsContent>
            <TabsContent value="canteen">
              <h3 className="mb-4 font-medium">Students in Canteen</h3>
              <StudentList students={mockStudentData.canteen} />
            </TabsContent>
            <TabsContent value="classroom">
              <h3 className="mb-4 font-medium">Students in Classroom</h3>
              <StudentList students={mockStudentData.classroom} />
            </TabsContent>
            <TabsContent value="lab">
              <h3 className="mb-4 font-medium">Students in Lab</h3>
              <StudentList students={mockStudentData.lab} />
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
    </div>
  );
};

export default LocationMonitor;
