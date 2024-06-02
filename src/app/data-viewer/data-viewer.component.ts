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

  inputValue: string = "";          // Bidirectional binding with row selection input element, stores the current value from input
  lastInputValue: string = "xxx";   // For optimization purposes to prevent unnecessary calls to backend that do not return different data
  inputErrorFlag: boolean = false;  // If input is incorrect and data not loaded properly, marks input bar as red
  
  infoText: string = "Przykład użycia:\n1-5, 20-40 (Wiersze 1-5 i 20-40)\n1-10, 12 (Wiersze 1-10 oraz 12-ty)\n# (Wszystkie wiersze)\n\n \
                      Domyślnie 100 pierwszych wierszy";

  constructor(private dataService: DataService) { }

  ngOnInit() {
    this.loadData();
  }

  loadData(selection: string = "") {
    this.dataService.getData(selection).subscribe({
      next: (data) => {
        this.data = data;
        this.inputErrorFlag = data.error;
      },
      error: (err) => console.error('Error fetching data:', err),
    });
  }

  onRefresh() {
    if (this.inputValue != this.lastInputValue) {
      console.log("XD");
      this.loadData(this.inputValue);
      this.lastInputValue = this.inputValue;
    }
  }
  
}
