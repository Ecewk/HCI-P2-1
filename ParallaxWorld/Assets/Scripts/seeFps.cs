using UnityEngine;
using System.Collections;
using UnityEngine.UI;

public class ShowFPS : MonoBehaviour
{
    public TMPro.TextMeshProUGUI fpsText;
    private float accumulatedDeltaTime = 0.0f;
    private int frameCount = 0;
    private string filePath = "fps.txt";

    void Start()
    {
        System.IO.File.AppendAllText(filePath, "-------------\n");
        InvokeRepeating("DisplayAndSaveFps", 1, 1);
    }

    void Update()
    {
        accumulatedDeltaTime += Time.unscaledDeltaTime;
        frameCount++;
    }

    void DisplayAndSaveFps()
    {
        float averageDeltaTime = accumulatedDeltaTime / frameCount;
        float fps = 1f / averageDeltaTime;
        fpsText.text = "FPS: " + Mathf.RoundToInt(fps).ToString();

        saveFps(fps);

        // Reset for the next interval
        accumulatedDeltaTime = 0f;
        frameCount = 0;
    }

    void saveFps(float fps)
    {
        System.IO.File.AppendAllText(filePath, Mathf.RoundToInt(fps).ToString() + "\n");
    }
}
