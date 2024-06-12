import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { CommonModule } from '@angular/common';
import { StartViewComponent } from './start-view/start-view.component';
import { DataViewerComponent } from './data-viewer/data-viewer.component';
import { PageNotFoundComponent } from './page-not-found/page-not-found.component';
import { DataNormalizationComponent } from './data-normalization/data-normalization.component';
import { PcaViewComponent } from './pca-view/pca-view.component';
import { ClusterViewComponent } from './cluster-view/cluster-view.component';

// Routing paths
const routes: Routes = [
   {path: '', component: StartViewComponent, data: { animation: 'OnePage' } },
   {path: 'data', component: DataViewerComponent, data: { animation: 'AnotherPage' }},
   {path: 'normalize', component: DataNormalizationComponent},
   {path: 'pca', component:PcaViewComponent},
   {path: 'cluster', component:ClusterViewComponent},
   {path: '**', component: PageNotFoundComponent}
   
];

@NgModule({
  imports: [RouterModule.forRoot(routes), CommonModule],
  exports: [RouterModule]
})

export class AppRoutingModule { }
