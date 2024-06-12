import { ComponentFixture, TestBed } from '@angular/core/testing';

import { PcaViewComponent } from './pca-view.component';

describe('PcaViewComponent', () => {
  let component: PcaViewComponent;
  let fixture: ComponentFixture<PcaViewComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [PcaViewComponent]
    });
    fixture = TestBed.createComponent(PcaViewComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
