using UnityEngine;

public class ChangeColors : MonoBehaviour
{
    [Header("Color Settings")]
    public Material blackMaterial;
    public Material whiteMaterial;
    public float switchInterval = 0.5f;
    
    private float timer;
    private Material[] uniqueMaterials;
    private Renderer[] renderers;
    private bool[] isCurrentlyWhite;

    void Start()
    {
        // Find all cubes
        GameObject[] cubes = GameObject.FindGameObjectsWithTag("ColorCube");
        
        uniqueMaterials = new Material[cubes.Length];
        renderers = new Renderer[cubes.Length];
        isCurrentlyWhite = new bool[cubes.Length];

        // Initialize each cube
        for (int i = 0; i < cubes.Length; i++)
        {
            renderers[i] = cubes[i].GetComponent<Renderer>();
            // Check initial material to determine if white
            isCurrentlyWhite[i] = renderers[i].material.name.Contains("White");
            // Create unique material instance
            uniqueMaterials[i] = new Material(renderers[i].material);
            renderers[i].sharedMaterial = uniqueMaterials[i];
        }
    }

    void Update()
    {
        timer += Time.deltaTime;

        if (timer >= switchInterval)
        {
            for (int i = 0; i < renderers.Length; i++)
            {
                // Toggle between black and white based on current state
                Material targetMaterial = isCurrentlyWhite[i] ? blackMaterial : whiteMaterial;
                renderers[i].sharedMaterial = targetMaterial;
                isCurrentlyWhite[i] = !isCurrentlyWhite[i];
            }
            timer = 0f;
        }
    }

    void OnDestroy()
    {
        if (uniqueMaterials != null)
        {
            foreach (Material mat in uniqueMaterials)
            {
                if (mat != null)
                    Destroy(mat);
            }
        }
    }
}