import { Component } from '@angular/core';
import { DataService } from '../data.service';
import { DataVisualization } from '../models/data.model';

@Component({
  selector: 'app-data-viewer',
  templateUrl: './data-viewer.component.html',
  styleUrls: ['./data-viewer.component.css']
})
export class DataViewerComponent {
  data: DataVisualization | null = null;

  constructor(private dataService: DataService) { }

  ngOnInit() {
    this.loadData();
  }

  loadData() {
    this.dataService.getData().subscribe({
      next: (data) => {
        this.data = data;
      },
      error: (err) => console.error('Error fetching data:', err),
    });
  }
}
