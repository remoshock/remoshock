# Pre release testing guide

Testing instruction before release.

<table border="1">

<tr>
<th>No</th>
<th>Action</th>
<th>Result</th>
</tr>


<tr>
<td>1.</td>
<td>Run <code>git status</code></td>
<td>No uncommited changes.</td>
</tr>


<tr>
<td>2.</td>
<td>Increase version number in <code>src/remoshock/core/version.py</code></td>
<td>-</td>
</tr>


<tr>
<td>3.</td>
<td>Run <code>./dist.sh</code></td>
<td>

- No error message
- Files <code>dist/remoshock-x.x.zip</code>, <code>dist/remoshock-x.x.tar.gz</code> and <code>remoshock-x.x-py3-none-any.whl</code> are created
- <code>git diff</code> shows only modification of the version number, and in REAME.md and version.py only.

</tr>


<tr>
<td>4.</td>
<td>

~~~~
rm ~/.config/remoshock.ini
mkdir -p ~/temp/remoshock
cd ~/temp/remoshock
python3 -m venv env
source env/bin/activate
pip3 install urh
pip3 uninstall remoshock
pip3 install ../../workspace/remoshock/dist/remoshock-*.whl
~~~~

</td>
<td>
Installation completes successfully
</td>
<tr>

<tr>
<td>5.</td>
<td>

- Run <code>remoshockcli</code>
- 1 HackRF
- 4 Receivers
- 1 PAC
- 1 PAC
- 4 Wodondog with light
- 3 Petrainer

</td>
<td>

- "Default configuration was written with random transmitter codes."
- In remoshock.ini, the variables web_authentication_token and transmitter_code contain random values.
- There is an example configuration for PAC, Wodondog and Petrainer receivers.
- There is an example configuration for the randomizer.
</td>
</tr>



<tr>
<td>6.</td>
<td>Reset PAC receiver into learning mode<br>
Run <code>remoshockcli</code></td>
<td>Receiver was paired to the new transmitter code, it stopped flashing red and started to blink green.</td>
</tr>


<tr>
<td>7.</td>
<td>Run <code>remoshockcli --sdr hackrfcli</code></code></td>
<td>The receiver beeps.</td>
</tr>


<tr>
<td>8.</td>
<td>Run <code>remoshockserver</code><br>
Open the displayed URL in a web-browser.</td>
<td>The remote-control website is shown.</td>
</tr>


<tr>
<td>9.</td>
<td>Click the BEEP-icon for the first receiver</td>
<td>The receiver beeps.</td>
</tr>


<tr>
<td>10.</td>
<td>Set duration to 1000ms and click the BEEP-SHOCK-icon for the first receiver.</td>
<td>The receiver beeps, there is a delay of 1 second, before the LIGHT flashes for another second.</td>
</tr>


<tr>
<td>11.</td>
<td>Reset Wodondog receiver into learning mode.<br>
Press the shock button for the first Wodondog receiver.</td>
<td>The receiver beeps, its stops flashing the light and starts blinking the light.</td>
</tr>


<tr>
<td>12.</td>
<td>Press the beep button for the first Wodondog receiver.</td>
<td>The receiver beeps.</td>
</tr>


<tr>
<td>13.</td>
<td>Wait five minutes</td>
<td>There are at least 2 automatic generated messages per Wodondog receiver. The message for each collar are at least 2 minutes and at most 2 minutes and 30 seconds apart.</td>
</tr>


<tr>
<td>14.</td>
<td>Press the beep button for the first Wodondog receiver.</td>
<td>The receiver beeps.</td>
</tr>


<tr>
<td>15.</td>
<td>Select application menu entry "Randomizer"</td>
<td>The randomizer configuration page is shown. Status: inactive</td>
</tr>


<tr>
<td>16.</td>
<td>Press "Start"</td>
<td>Status: active. The console shows a beep sent to each receiver.</td>
</tr>


<tr>
<td>17.</td>
<td>Press "Stop"</td>
<td>Status: stopped. The console says: "Randomizer canceled</td>
</tr>


<tr>
<td>18.</td>
<td>Select application menu entry "Gamepad"</td>
<td>A text asks for pressing a button</td>
</tr>


<tr>
<td>19.</td>
<td>Click "Gamepad mapping"</td>
<td>-</td>
</tr>


<tr>
<td>20.</td>
<td>Configure the gamepad and click save</td>
<td>-</td>
</tr>


<tr>
<td>21.</td>
<td>Test the gamepad mapping</td>
<td>The pressed buttons are highlighted.</td>
</tr>


<tr>
<td>22.</td>
<td>End the remoshockserver-process by pressing <code>ctrl+c</code></td>
<td>No error message is shown. No traceback is shown.</td>
</tr>


<tr>
<td>23.</td>
<td>Edit remoshock.ini to setup the following randomizer configuration:

~~~~
[randomizer]
beep_probability_percent = 100
shock_probability_percent = 100
shock_min_duration_ms = 250
shock_max_duration_ms = 500
shock_min_power_percent = 5
shock_max_power_percent = 10
pause_min_s = 3
pause_max_s = 5
start_delay_min_minutes = 0
start_delay_max_minutes = 1
runtime_min_minutes = 2
runtime_max_minutes = 3

~~~~

</td>
<td>-</td>
</tr>


<tr>
<td>24.</td>
<td>Run <code>remoshockrnd --mock</code></td>
<td>

- A beep is sent to 4 collars, about a second apart.<br>
- After the last beep and before the first BEEPSHOCK, there is a delay of less than 65 seconds<br>
- There are BEEPSHOCK-message for all 4 collars
- Power varies between 5% and 10%
- Duration varies between the two exact values 250ms and 500ms
- The last BEEPSHOCK-message is between 120s and 185ms of the first BEEPSHOCK-message
- The programm ends with "Runtime completed".
</td>
</tr>

</table>

# Publish release

- create GitHub-releases with change-notes, a tag starting with "v" followed by the version number
- upload build/remoshock-x.x.zip to the release
- upload to pip

~~~~
python3 -m twine upload dist/*.tar.gz dist/*.whl
git commit -am "released version x.x"
git push
git checkout -b VERSION_xx_RELEASE_xx
git push --set-upstream origin VERSION_xx_RELEASE_xx
git checkout master
~~~~

