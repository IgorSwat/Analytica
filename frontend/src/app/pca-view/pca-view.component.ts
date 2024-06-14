import { Component } from '@angular/core';
import { DataService } from '../data.service';
import { PcaData } from '../models/data.model';
import { trigger, state, style, transition, animate, query, stagger } from '@angular/animations';

@Component({
  selector: 'app-pca-view',
  templateUrl: './pca-view.component.html',
  styleUrls: ['./pca-view.component.css']
})


export class PcaViewComponent {
  // Main data container
  pcaData: PcaData | null = null;

  // Number of components input elements
  noComponents: number = 0;
  prevNoComponents: number = 2;
  inputErrorFlag: boolean = false;

  // Plot state
  plotImage: string | null = null;
  currentPlot: number = 0;
  MAX_NO_PLOTS: number = 3;

  // GUI text elements
  infoText1 = "PCA - metoda redukcji wymiarowości poprzez zastępowanie cech tzw. \"składowymi głównymi\"\n\n" +
              "Wybierz liczbę składowych głównych do dalszej analizy." 


  // --------------
  // Initialization
  // --------------

  constructor(private dataService: DataService) { }

  ngOnInit() {
    this.refreshData();
  }


  // ------------
  // API handlers
  // ------------

  loadPcaData() : void {
    this.dataService.getPcaData(this.noComponents).subscribe({
      next: (data) => {
        this.pcaData = data;
        this.noComponents = data.noComponents;
        this.prevNoComponents = this.noComponents;
        this.inputErrorFlag = data.error;
      },
      error: (err) => console.error('Error fetching data:', err)
    });
  }

  loadPlot() : void {
    this.dataService.getPcaPlot(this.currentPlot).subscribe({
      next: (response) => {
        this.plotImage = "data:image/png;base64," + response.image;
      },
      error: (err) => console.error('Error fetching data:', err)
    });
  }


  // --------------
  // Action methods
  // --------------

  prevPlot() : void {
    this.currentPlot = (this.currentPlot - 1) % this.MAX_NO_PLOTS;
    this.loadPlot();
  }

  nextPlot() : void {
    this.currentPlot = (this.currentPlot + 1) % this.MAX_NO_PLOTS;
    this.loadPlot();
  }

  saveImage() : void {
    if (this.plotImage != null) {
      const link = document.createElement('a');
      link.href = this.plotImage;
      link.download = "plot.png";
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  }

  refreshData() : void {
    this.loadPcaData();
    this.loadPlot();
  }


  // -----------------------
  // Getters and comparators
  // -----------------------

  hasNoComponentsChanged() : boolean {
    return this.noComponents != this.prevNoComponents;
  }

}
