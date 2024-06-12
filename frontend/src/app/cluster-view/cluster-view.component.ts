import { Component } from '@angular/core';
import { DataService } from '../data.service';
import { ClusterInfo } from '../models/data.model';

@Component({
  selector: 'app-cluster-view',
  templateUrl: './cluster-view.component.html',
  styleUrls: ['./cluster-view.component.css']
})
export class ClusterViewComponent {
  clusterInfo: ClusterInfo | null = null;

  featureStates: boolean[] = new Array(20).fill(true);

  // Plot state
  plotImage: string | null = null;
  currentPlot: number = 0;
  MAX_NO_PLOTS: number = 3;

  // Info text
  infoText1 = "Wybierz zmienne do grupowania";

  constructor(private dataService: DataService) { }

  ngOnInit() {
    this.loadClusterInfo();
    this.loadPlot();
  }

  loadClusterInfo() : void {
    this.dataService.getClusterInfo().subscribe({
      next: (clusterInfo) => {
        this.clusterInfo = clusterInfo;
      },
      error: (err) => console.error('Error fetching data:', err)
    });
  }

  loadPlot() : void {
    this.dataService.getClusterPlot(this.currentPlot).subscribe({
      next: (response) => {
        this.plotImage = "data:image/png;base64," + response.image;
        console.log("Plot succesfully loaded")
      },
      error: (err) => console.error('Error fetching data:', err)
    });
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
