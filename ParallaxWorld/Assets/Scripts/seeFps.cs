using UnityEngine;
using System.Collections;
using UnityEngine.UI;

//to see the fps in the game
public class showFPS : MonoBehaviour {
	public Text fpsText;
	public float deltaTime;

	void Update () {
		deltaTime += (Time.deltaTime - deltaTime) * 0.1f;
		float fps = 1.0f / deltaTime;
		fpsText.text = Mathf.Ceil (fps).ToString ();
	}
}