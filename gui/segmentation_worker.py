from PyQt5.QtCore import QThread, pyqtSignal

class SegmentationWorker(QThread):
    finished = pyqtSignal(dict)
    progress = pyqtSignal(int)
    status = pyqtSignal(str)
    error = pyqtSignal(str)
    
    def __init__(self, segmentation_controller, points_by_slice, dimension):
        super().__init__()
        self.segmentation_controller = segmentation_controller
        self.points_by_slice = points_by_slice
        self.dimension = dimension
        self._is_cancelled = False
        
    def run(self):
        try:
            # Emit initial progress
            self.segmentation_controller.progress_callback = self.progress.emit
            self.segmentation_controller.status_callback = self.status.emit
            
            masks = self.segmentation_controller.run_segmentation(
                points_by_slice=self.points_by_slice,
                dimension=self.dimension
            )
            
            if self._is_cancelled:
                return
                
            self.finished.emit(masks)
            
        except Exception as e:
            self.error.emit(str(e))
            
    def cancel(self):
        """Cancel the segmentation worker."""
        self._is_cancelled = True
        self.segmentation_controller.cancel_segmentation()
        self.quit()