using UnityEngine;

public class camScript : MonoBehaviour
{
    private static camScript cam;

    // Start is called once before the first execution of Update after the MonoBehaviour is created
    void Start()
    {
        
    }

    void Awake()
    {
        if (cam == null) {
            cam = this;
            DontDestroyOnLoad(cam);
        }
        else {
            Destroy(gameObject);
        }
    } 

    // Update is called once per frame
    void Update()
    {
        
    }
}
