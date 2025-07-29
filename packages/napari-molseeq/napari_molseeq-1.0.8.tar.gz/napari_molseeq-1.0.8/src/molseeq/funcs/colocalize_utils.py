import traceback
import numpy as np
import cv2
from molseeq.funcs.utils_compute import Worker


class _utils_colocalize:

    def filter_locs_by_matches(self, locs, coords, matches):

        try:

            locs = locs.copy()
            coords = coords.copy()
            matches = matches.copy()

            coords = np.float32([coords[m.queryIdx] for m in matches]).reshape(-1, 2)

            filtered_locs = []

            for loc in locs:
                coord = [loc.x, loc.y]
                if coord in coords.tolist():
                    filtered_locs.append(loc)

            filtered_locs = np.rec.fromrecords(filtered_locs, dtype=locs.dtype)

        except:
            print(traceback.format_exc())
            filtered_locs = None
            pass

        return filtered_locs





    def _molseeq_colocalize_localisations(self, progress_callback=None):

        try:

            dataset = self.gui.colo_dataset.currentText()
            channel1 = self.gui.colo_channel1.currentText()
            channel2 = self.gui.colo_channel2.currentText()
            max_dist = float(self.gui.colo_max_dist.currentText())

            ch1_loc_dict, ch1_n_locs, _ = self.get_loc_dict(dataset, channel1.lower())
            ch2_loc_dict, ch2_n_locs, _ = self.get_loc_dict(dataset, channel2.lower())

            ch1_locs = ch1_loc_dict["localisations"].copy()
            ch2_locs = ch2_loc_dict["localisations"].copy()

            ch1_coords = [[loc.x, loc.y] for loc in ch1_locs]
            ch2_coords = [[loc.x, loc.y] for loc in ch2_locs]

            ch1_coords = np.array(ch1_coords).astype(np.float32)
            ch2_coords = np.array(ch2_coords).astype(np.float32)

            bf = cv2.BFMatcher(cv2.NORM_L1, crossCheck=True)

            matches = bf.match(ch1_coords, ch2_coords)
            matches = [m for m in matches if m.distance < max_dist]

            ch1_coords = np.float32([ch1_coords[m.queryIdx] for m in matches]).reshape(-1, 2)
            ch2_coords = np.float32([ch2_coords[m.trainIdx] for m in matches]).reshape(-1, 2)

            filtered_ch1_locs = []

            for loc in ch1_locs:
                coord = [loc.x, loc.y]
                if coord in ch1_coords.tolist():
                    filtered_ch1_locs.append(loc)

            filtered_ch1_locs = np.rec.fromrecords(filtered_ch1_locs, dtype=ch1_locs.dtype)

            filtered_ch2_locs = []

            for loc in ch2_locs:
                coord = [loc.x, loc.y]
                if coord in ch2_coords.tolist():
                    filtered_ch2_locs.append(loc)

            filtered_ch2_locs = np.rec.fromrecords(filtered_ch2_locs, dtype=ch2_locs.dtype)

            colo_locs = []

            for loc1, loc2 in zip(filtered_ch1_locs, filtered_ch2_locs):
                locX = (loc1.x + loc2.x) / 2
                locY = (loc1.y + loc2.y) / 2

                colo_loc = loc1.copy()
                colo_loc.x = locX
                colo_loc.y = locY

                colo_locs.append(colo_loc)

            colo_locs = np.rec.fromrecords(colo_locs, dtype=filtered_ch1_locs.dtype)

            result_dict = {"localisations": colo_locs}

            self.molseeq_notification(f"Found {len(colo_locs)} colocalisations between {channel1} and {channel2}")

        except:
            print(traceback.format_exc())
            ch1_result_dict = None
            ch2_result_dict = None
            result_dict = None
            pass

        return result_dict

    def _molseeq_colocalize_localisations_result(self, colo_locs):

        try:

            if colo_locs is not None:

                dataset = self.gui.colo_dataset.currentText()
                channel1 = self.gui.colo_channel1.currentText()
                channel2 = self.gui.colo_channel2.currentText()

                if self.gui.colo_fiducials.isChecked():

                    self.localisation_dict["localisations"][dataset][channel1.lower()]["localisations"] = colo_locs["localisations"]
                    self.localisation_dict["localisations"][dataset][channel2.lower()]["localisations"] = colo_locs["localisations"]

                    self.draw_localisations(update_vis=True)

                if self.gui.colo_bboxes.isChecked():

                    self.localisation_dict["bounding_boxes"]["localisations"] = colo_locs["localisations"]

                    self.draw_bounding_boxes()

        except:
            print(traceback.format_exc())
            pass

    def _molseeq_colocalize_localisations_finished(self):

        self.update_ui()


    def molseeq_colocalize_localisations(self):

        try:

            dataset = self.gui.colo_dataset.currentText()
            channel1 = self.gui.colo_channel1.currentText()
            channel2 = self.gui.colo_channel2.currentText()

            ch1_loc_dict, ch1_n_locs, _ = self.get_loc_dict(dataset, channel1.lower())
            ch2_loc_dict, ch2_n_locs, _ = self.get_loc_dict(dataset, channel2.lower())

            if channel1 == channel2:
                self.molseeq_notification("Channels must be different for colocalisation")

            elif ch1_n_locs == 0 or ch2_n_locs == 0:
                self.molseeq_notification("No localisations found in one or both channels.")

            else:
                self.update_ui(init=True)

                self.worker = Worker(self._molseeq_colocalize_localisations)
                self.worker.signals.result.connect(self._molseeq_colocalize_localisations_result)
                self.worker.signals.finished.connect(self._molseeq_colocalize_localisations_finished)
                self.worker.signals.error.connect(self.update_ui)
                self.threadpool.start(self.worker)

        except:
            print(traceback.format_exc())
            pass


