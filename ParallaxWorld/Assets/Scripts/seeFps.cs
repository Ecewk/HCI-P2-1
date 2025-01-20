using UnityEngine;
using System.Collections;
using UnityEngine.UI;

//to see the fps in the game
public class showFPS : MonoBehaviour {
	public TMPro.TextMeshProUGUI fpsText;
	private float fps;
	private string filePath = "fps.txt";


	void Start () {
		System.IO.File.AppendAllText(filePath,"-------------\n");
		InvokeRepeating("GetFps", 1, 1);
	}
	void GetFps(){
		fps = (int)(1f / Time.unscaledDeltaTime);
		fpsText.text = "FPS: " + fps.ToString();
		saveFps();

	}
	void saveFps(){
		System.IO.File.AppendAllText(filePath, fps.ToString() + "\n");
	}
}