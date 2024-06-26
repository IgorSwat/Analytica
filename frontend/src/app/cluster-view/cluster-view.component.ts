import { Component } from '@angular/core';
import { DataService } from '../data.service';
import { ClusterData } from '../models/data.model';
import { ClusteringQuality} from '../models/clustering-quality';

@Component({
  selector: 'app-cluster-view',
  templateUrl: './cluster-view.component.html',
  styleUrls: ['./cluster-view.component.css']
})

export class ClusterViewComponent {
  // Main data container
  clusterData: ClusterData | null = null;

  // Data download menu view
  downloadMenuState: boolean = false;

  // Main input value
  clustering_method: string = "";
  // Other input values
  n_clusters: number = 2;
  eps: number = 1.5;
  min_samples: number = 2;
  linkage: string = "ward";
  // Select options
  availableMethods = ["k-means", "dbscan", "agglomerate"];
  availableLinkage = ["ward", "complete", "average", "single"];

  // Plot data
  plotImage: string | null = null;

  // Quality label
  quality: ClusteringQuality = ClusteringQuality.NONE;
  qualityLabel: string = "NIEZNANY";

  // Main input tooltip
  kMeansInfo: string = "K-Means: iteracyjny algorytm klasteryzacji realizujący następujące kroki:\n" +
                       "  1. Wybór k początkowych centroidów\n" +
                       "  2. Przypisanie każdego punktu do najbliższego z centroidów\n" +
                       "  3. Przeliczenie nowych centroidów jako średnich punktów przypisanych do każdego klastra\n" +
                       "Powyższy proces powtarzany jest do momentu, aż centroidy przestaną się zmieniać lub osiągnięta\n" +
                       "zostanie maksymalna liczba iteracji.";
  dbscanInfo: string = "DBSCAN (Density-Based Spatial Clustering of Applications with Noise): metoda klasteryzacji oparta na gęstości.\n" +
                       "Wybierany jest punkt rdzeniowy - punkt, który ma co najmniej 'min_samples' punktów w promieniu 'eps'.\n" +
                       "Rozpoczynając od punktu rdzeniowego, algorytm iteracyjnie odwiedza kolejne punkty tworząc klastry,\n" +
                       "aż nie znajdzie więcej punktów spełniających warunek gęstości.";
  agglomerateInfo: string = "Agglomerative Clustering: klasteryzacja hierarchiczna, polegająca na łączeniu mniejszych klastrów w większe.\n" +
                            "Początkowo, każdy punkt zaczyna jako osobny klaster. W kolejnych iteracjach, dwa najbliższe klastry\n" +
                            "łączone są w jeden większy klaster. Procxes powtarza się do momentu pogrupowania wszystkich punktów\n" +
                            "lub osiągnięcia podanej liczby klastrów.";
  clusteringMethodInfo: string = this.kMeansInfo;  // Currently shown info text (one of the above 3)
  // Secondary input tooltips
  nClustersInfo: string = "Docelowa liczba klastrów";
  epsInfo: string = "Maksymalna odległość dla których 2 punkty są uznawane za sąsiadujące";
  minSamplesInfo: string = "Minimalna liczba punktów potrzebna do utworzenia gęstego rejonu";
  linkageInfo: string = "Kryterium łączenia klastrtów:\n" +
                        "'ward': minimalizacja wariancji w klastrach\n" +
                        "'complete': odległość między klastrami jako max odległość między parami punktów z danych klastrów\n" +
                        "'average': odległość między klastrami jako średnia z odległości między parami punktów z danych klastrów\n" +
                        "'single': odległość między klastrami jako min odległość między parami punktów z danych klastrów";
  // Metrics info
  silhouetteInfo: string = "Mierzy jak dobrze obiekty przypisane są do swoich klastrów w porównaniu do innych klastrów.\n\n" +
                           "Czym wyższa wartość, tym lepsza jakość klasteryzacji.";
  daviesBouldinInfo: string = "Oblicza wskaźnik podobieństwa na podstawie odległości (M) i rozproszenia (S) wewnątrz klastrów.\n\n" +
                              "Czym niższa wartość, tym lepsza jakość klasteryzacji.";


  // --------------
  // Initialization
  // --------------

  constructor(private dataService: DataService) {}

  ngOnInit() {
    this.loadClusteringData();
    this.loadPlot();
  }


  // ------------
  // API handlers
  // ------------

  loadClusteringData() : void {
    this.dataService.clusterizeData(this.clustering_method, this.n_clusters, this.eps, this.min_samples, this.linkage).subscribe({
      next: (data) => {
        this.clusterData = data;
        this.clustering_method = data.clustering_method;
        this.n_clusters = data.n_clusters;
        this.eps = data.eps;
        this.min_samples = data.min_samples;
        this.linkage = data.linkage;
        this.setQuality(data.quality);
      },
      error: (err) => console.error('Error fetching data:', err)
    });
  }

  loadPlot() : void {
    this.dataService.getClusterPlot().subscribe({
      next: (response) => {
        this.plotImage = "data:image/png;base64," + response.image;
      },
      error: (err) => console.error('Error fetching data:', err)
    })
  }

  downloadData(rawFlag: boolean) : void {
    if (this.clusterData != null) {
      this.dataService.downloadClusterData(rawFlag).subscribe({
        next: (response) => {
          // Create CSV file representation
          const file = new Blob([response], { type: 'text/csv' });
        
          // Create virtual link
          const link = document.createElement('a');
          link.href = window.URL.createObjectURL(file);
          link.download = 'data.csv';
          link.click();

          this.setDownloadMenuState(false);
        },
        error: (err) => console.error('Error fetching data:', err)
      })
    }
  }


  // --------------
  // Action methods
  // --------------

  refreshData() : void {
    if (this.clustering_method == "k-means" && this.validate_n_clusters())
      console.log("XD");
    if ((this.clustering_method == "k-means" && this.validate_n_clusters()) ||
        (this.clustering_method == "dbscan" && this.validate_eps() && this.validate_min_samples()) ||
        (this.clustering_method == "agglomerate" && this.validate_n_clusters())) {
      this.loadClusteringData();
      this.loadPlot();
    }
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

  onMethodChange(method: string) : void {
    this.clusteringMethodInfo = method == "k-means" ? this.kMeansInfo :
                                method == "dbscan" ? this.dbscanInfo :
                                method == "agglomerate" ? this.agglomerateInfo : "";
  }

  setDownloadMenuState(state: boolean) : void {
    this.downloadMenuState = state;
  }

  private setQuality(q: number) : void {
    const mapping: {[key: number]: string} = {
      0: "NIEZNANA",
      1: "ZŁA",
      2: "ŚREDNIA",
      3: "DOBRA",
      4: "DOSKONAŁA"
    };

    this.quality = <ClusteringQuality>q;
    this.qualityLabel = mapping[q];
  }


  // -----------------------
  // Getters and comparators
  // -----------------------

  validate_n_clusters() : boolean {
    return this.n_clusters >= 1 && (!this.clusterData || this.n_clusters <= this.clusterData.length);
  }

  validate_eps() : boolean {
    return this.eps > 0;
  }

  validate_min_samples() : boolean {
    return this.min_samples > 1;
  }

  hasInputChanged() : boolean {
    if (!this.clusterData)
      return false;
    if (this.clusterData.clustering_method != this.clustering_method)
      return true;
    if (this.clustering_method == "k-means")
      return this.clusterData.n_clusters != this.n_clusters;
    if (this.clustering_method == "dbscan")
      return this.clusterData.eps != this.eps || this.clusterData.min_samples != this.min_samples;
    if (this.clustering_method == "agglomerate")
      return this.clusterData.n_clusters != this.n_clusters || this.clusterData.linkage != this.linkage;
    return false;
  }

}
