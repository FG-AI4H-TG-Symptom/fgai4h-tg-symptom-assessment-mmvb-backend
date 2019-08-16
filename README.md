
# Intro and Note

This is the minimal minimal viable benchmark (MMVB) designed and developed by the members of the sub-group (topic group) “Symptom assessment”, which is the part of the ITU focus group “Artificial Intelligence for Health”. The minimal minimal viable benchmark is a prototype and does not reflect in any possible way real methods, techniques, approaches, etc. that the members (including commercial companies) use in their products.

As mentioned on [the focus group website](https://www.itu.int/en/ITU-T/focusgroups/ai4h/Pages/default.aspx): “The ITU/WHO Focus Group on artificial intelligence for health (FG-AI4H) works in partnership with the World Health Organization (WHO) to establish a standardized assessment framework for the evaluation of AI-based methods for health, diagnosis, triage or treatment decisions. Participation in the FG-AI4H is free of charge and open to all.”



# How to run

```python
mkvirtualenv your-name-for-a-python-virtual-environment
pip install -r requirements.txt
python3 run_all.py
```
and then go to http://127.0.0.1:5005/ for the main web interface.

You also can access individual end-points:
* Case generator: http://127.0.0.1:5001/case-generator/v1/ui/
* Toy AI implementations: http://127.0.0.1:5002/toy-ai/v1/ui/
* Evaluator of AI results against cases: http://127.0.0.1:5003/evaluator/v1/ui/
* Metric calculators: http://127.0.0.1:5004/metric-calculator/v1/ui/

API specification can be found in `/swagger/` folder.


# Tests

There are several tests included to verify the functionality of the
different components of the MMVB. To set up your environment for testing,
activate your virtual environment and run:
```
pip install -r tests/requirements.txt
```
To run the tests, run:
```
pytest
```

# Copyright and Licence

Copyright, 2019, created jointly by the members of the ITU sub-group (topic group) "Symptom assessment" of the International Telecommunication Union focus group “Artificial Intelligence for Health”, which works in partnership with the World Health Organisation.

All parts of this benchmark are free software: you can redistribute them and/or modify them under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

They are distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.
