import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { HttpClientModule } from '@angular/common/http';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { NavbarComponent } from './navbar/navbar.component';
import { StartViewComponent } from './start-view/start-view.component';
import { PageNotFoundComponent } from './page-not-found/page-not-found.component';
import { DataViewerComponent } from './data-viewer/data-viewer.component';
import { DataNormalizationComponent } from './data-normalization/data-normalization.component';

@NgModule({
  declarations: [
    AppComponent,
    NavbarComponent,
    StartViewComponent,
    PageNotFoundComponent,
    DataViewerComponent,
    DataNormalizationComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    FormsModule,
    HttpClientModule,
    ReactiveFormsModule
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
