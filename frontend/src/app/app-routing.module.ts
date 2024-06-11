import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { CommonModule } from '@angular/common';
import { StartViewComponent } from './start-view/start-view.component';
import { DataViewerComponent } from './data-viewer/data-viewer.component';
import { PageNotFoundComponent } from './page-not-found/page-not-found.component';
import { DataNormalizationComponent } from './data-normalization/data-normalization.component';
import { PcaViewComponent } from './pca-view/pca-view.component';

// Routing paths
const routes: Routes = [
   {path: '', component: StartViewComponent},
   {path: 'data', component: DataViewerComponent},
   {path: 'normalize', component: DataNormalizationComponent},
   {path: 'pca', component:PcaViewComponent},
   {path: '**', component: PageNotFoundComponent}
   
];

@NgModule({
  imports: [RouterModule.forRoot(routes), CommonModule],
  exports: [RouterModule]
})

export class AppRoutingModule { }
