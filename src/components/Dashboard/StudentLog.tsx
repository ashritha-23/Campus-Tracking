
import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Select, SelectTrigger, SelectValue, SelectContent, SelectItem } from "@/components/ui/select";
import { Search, Download, RefreshCw } from "lucide-react";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { useToast } from "@/components/ui/use-toast";

// API base URL - change this to match your Flask server
const API_BASE_URL = "http://localhost:5000/api";

const StudentLog = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [locationFilter, setLocationFilter] = useState('all');
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(false);
  const { toast } = useToast();
  
  const fetchLogs = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/logs`);
      
      if (!response.ok) {
        throw new Error('Failed to fetch logs');
      }
      
      const data = await response.json();
      setLogs(data.logs || []);
    } catch (error) {
      toast({
        title: "Error fetching logs",
        description: error.message || "Something went wrong",
        variant: "destructive",
      });
      // Use mock data as fallback
      setLogs(mockLogs);
    } finally {
      setLoading(false);
    }
  };
  
  useEffect(() => {
    fetchLogs();
  }, []);
  
  // Filter logs based on search query and location filter
  const filteredLogs = logs.filter(log => {
    const matchesSearch = 
      log.person_id?.toLowerCase().includes(searchQuery.toLowerCase()) || 
      log.person_name?.toLowerCase().includes(searchQuery.toLowerCase());
      
    const matchesLocation = locationFilter === 'all' || log.location === locationFilter;
    
    return matchesSearch && matchesLocation;
  });

  const handleDownloadCSV = () => {
    // Convert logs to CSV format
    const headers = ["Timestamp", "Student ID", "Name", "Location"];
    const csvContent = [
      headers.join(','),
      ...filteredLogs.map(log => 
        [log.timestamp, log.person_id, log.person_name, log.location].join(',')
      )
    ].join('\n');
    
    // Create a Blob and trigger download
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `student_logs_${new Date().toISOString().slice(0,10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Student Activity Logs</CardTitle>
          <CardDescription>
            Review all student tracking data from the system
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="mb-6 flex flex-col sm:flex-row items-center gap-4">
            <div className="relative w-full sm:w-72">
              <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search by ID or name..."
                className="pl-8"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
            
            <Select value={locationFilter} onValueChange={setLocationFilter}>
              <SelectTrigger className="w-full sm:w-40">
                <SelectValue placeholder="All Locations" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Locations</SelectItem>
                <SelectItem value="Library">Library</SelectItem>
                <SelectItem value="Canteen">Canteen</SelectItem>
                <SelectItem value="Classroom">Classroom</SelectItem>
                <SelectItem value="Lab">Lab</SelectItem>
              </SelectContent>
            </Select>
            
            <div className="flex gap-2 ml-auto">
              <Button
                variant="outline"
                size="icon"
                onClick={fetchLogs}
                disabled={loading}
              >
                <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
              </Button>
              
              <Button
                variant="outline"
                size="icon"
                onClick={handleDownloadCSV}
                disabled={loading}
              >
                <Download className="h-4 w-4" />
              </Button>
            </div>
          </div>

          <div className="rounded-md border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>ID</TableHead>
                  <TableHead>Name</TableHead>
                  <TableHead>Location</TableHead>
                  <TableHead className="hidden md:table-cell">Timestamp</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredLogs.map((log, index) => (
                  <TableRow key={index}>
                    <TableCell className="font-medium">{log.person_id}</TableCell>
                    <TableCell>{log.person_name}</TableCell>
                    <TableCell>{log.location}</TableCell>
                    <TableCell className="hidden md:table-cell">{log.timestamp}</TableCell>
                  </TableRow>
                ))}
                {filteredLogs.length === 0 && (
                  <TableRow>
                    <TableCell colSpan={4} className="text-center py-6 text-muted-foreground">
                      {loading ? 'Loading logs...' : 'No records found'}
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

// Mock log data as fallback
const mockLogs = [
  { person_id: 'S001', person_name: 'John Smith', location: 'Library', timestamp: '2023-05-19 09:15:22' },
  { person_id: 'S012', person_name: 'Emily Johnson', location: 'Library', timestamp: '2023-05-19 09:22:45' },
  { person_id: 'S023', person_name: 'Jessica Taylor', location: 'Canteen', timestamp: '2023-05-19 12:10:33' },
  { person_id: 'S034', person_name: 'Matthew Thomas', location: 'Classroom', timestamp: '2023-05-19 11:00:12' },
  { person_id: 'S045', person_name: 'Michael Brown', location: 'Library', timestamp: '2023-05-19 09:30:55' },
  { person_id: 'S056', person_name: 'Daniel Martinez', location: 'Canteen', timestamp: '2023-05-19 12:15:03' },
  { person_id: 'S067', person_name: 'Sarah Davis', location: 'Library', timestamp: '2023-05-19 09:45:18' },
  { person_id: 'S078', person_name: 'Sophia Anderson', location: 'Canteen', timestamp: '2023-05-19 12:25:41' },
  { person_id: 'S089', person_name: 'David Wilson', location: 'Library', timestamp: '2023-05-19 10:05:09' },
  { person_id: 'S045', person_name: 'Michael Brown', location: 'Classroom', timestamp: '2023-05-19 11:00:30' },
  { person_id: 'S089', person_name: 'David Wilson', location: 'Classroom', timestamp: '2023-05-19 11:05:22' },
  { person_id: 'S012', person_name: 'Emily Johnson', location: 'Classroom', timestamp: '2023-05-19 11:10:15' },
  { person_id: 'S067', person_name: 'Sarah Davis', location: 'Lab', timestamp: '2023-05-19 14:15:50' },
  { person_id: 'S078', person_name: 'Sophia Anderson', location: 'Lab', timestamp: '2023-05-19 14:20:27' },
];

export default StudentLog;
