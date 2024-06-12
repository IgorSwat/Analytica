import { Component } from '@angular/core';
import { DataService } from '../data.service';
import { PcaInfo } from '../models/data.model';

@Component({
  selector: 'app-pca-view',
  templateUrl: './pca-view.component.html',
  styleUrls: ['./pca-view.component.css']
})
export class PcaViewComponent {
  pcaInfo: PcaInfo | null = null;

  featureStates: boolean[] = new Array(20).fill(true);

  // Plot state
  plotImage: string | null = null;
  currentPlot: number = 0;
  MAX_NO_PLOTS: number = 3;

  // Info text
  infoText1 = "Wybierz zmienne do grupowania";

  constructor(private dataService: DataService) { }

  ngOnInit() {
    this.loadPcaInfo();
    this.loadPlot();
  }

  loadPcaInfo() : void {
    this.dataService.getPcaInfo().subscribe({
      next: (pcaInfo) => {
        this.pcaInfo = pcaInfo;
        this.featureStates = [...this.pcaInfo.selections];
      },
      error: (err) => console.error('Error fetching data:', err)
    });
  }

  loadPlot() : void {
    this.dataService.getPcaPlot(this.currentPlot).subscribe({
      next: (response) => {
        this.plotImage = "data:image/png;base64," + response.image;
        console.log("Plot succesfully loaded")
      },
      error: (err) => console.error('Error fetching data:', err)
    });
  }

  updateFeatureSelection() : void {
    this.dataService.updateFeatureSelection(this.featureStates).subscribe({
      next: (response) => {
        console.log(response);
        this.loadPcaInfo();
      },
      error: (err) => console.error('Error fetching data:', err)
    });
  }

  isFeatureSelectionChanged() : boolean {
    for (let i = 0; i < this.featureStates.length; i++) {
      if (this.featureStates[i] != this.pcaInfo?.selections[i])
        return true;
    }
    return false;
  }

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

}
